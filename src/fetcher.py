"""
Scrape runs from repositories, store them into MongoDB and push repo name to RabbitMQ for further processing (e.g., download logs)
"""

import logging
import os
from datetime import datetime

import pymongo
from pymongo.errors import DuplicateKeyError
from pythonjsonlogger import jsonlogger
from tqdm import tqdm

from src.api.github import GithubApi
from src.tools.mq import PikaWrapper

# Setup logging
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

if os.environ.get("JSON_LOGS") == "true":
    json_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s")
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(json_formatter)
    logging.getLogger().handlers.clear()
    logging.getLogger().addHandler(log_handler)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG if os.environ.get("DEBUG", "false") == "true" else logging.INFO)

MONGO_CLIENT = pymongo.MongoClient(
    host=os.environ.get("MONGODB_HOST", "127.0.0.1"),
    port=int(os.environ.get("MONGODB_PORT", "27017")),
)
MONGO_REPOSITORIES = MONGO_CLIENT["gha-scraper"]["repositories"]
MONGO_RUNS = MONGO_CLIENT["gha-scraper"]["runs"]

PIKA_WRAPPER = PikaWrapper("fetcher")

GITHUB_API_ONE_TOKEN = GithubApi(config_path="secrets/github_fetcher.yaml")
GITHUB_API_POOL_TOKENS = GithubApi()


def process_repo(repo) -> None:
    """
    Process a repo
    """

    logger = logging.LoggerAdapter(LOGGER, extra={"repo_name": repo["_id"]})


    # Check if there is new runs using conditional requests (Etag)
    etag_db = MONGO_REPOSITORIES.find_one({"_id": repo["_id"]}, projection={"etag": True}).get("etag")
    new_runs_present, etag = GITHUB_API_ONE_TOKEN.check_new_runs(repo["_id"], etag_db)

    if new_runs_present is False:
        logger.info("Etag matched: no new run to scrape")
        return

    # If Etag was not defined or a new etag was returned: update Etag in db
    MONGO_REPOSITORIES.update_one({"_id": repo["_id"]}, {"$set": {"etag": etag}})

    # Scrape runs only until the latest imported run
    latest_scraped_run = next(
            MONGO_RUNS.find(
            {"repository_name": repo["_id"]},
            projection={"metadata.created_at": True},
            sort=[("metadata.created_at", -1)],
            limit=1
        )
    )
    logger.info("latest scraped run: %s", latest_scraped_run)

    if latest_scraped_run and not os.environ.get("FORCE_SCRAPE_ALL_RUNS") == "true":
        from_date = datetime.strptime(latest_scraped_run["metadata"]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    else:  # Never seen before repo
        LOGGER.info("No previous run for %s or FORCE_SCRAPE_ALL_RUNS enabled", repo["_id"])
        from_date = None  # Default to -90d

    new_runs = GITHUB_API_POOL_TOKENS.get_workflow_runs(repo["_id"], from_date=from_date, group_by_workflow=False, limit=10000)
    logger.info("%d new runs found for %s", len(new_runs), repo["_id"])

    inserted_runs_count = 0
    for run in new_runs:
        # We are only interested in runs that have a log, i.e., not pending, action_required or similar runs
        # Don't insert action_required runs else they will not be inserted later because DuplicateKeyError
        if run["conclusion"] not in ["success", "failure", "timed_out"]:
            LOGGER.debug("Run %d ignored because conclusion=%s", run["id"], run["conclusion"])
            continue

        try:
            run_uid = f"{run['repository']['full_name']}_{run['path']}_{run['run_number']}_{run['run_attempt']}"
            MONGO_RUNS.insert_one(
                {
                    "_id": run_uid,
                    "repository_name": run["repository"]["full_name"],
                    "workflow_path": run["path"],
                    "run_number": run["run_number"],
                    "run_attempt": run["run_attempt"],
                    "time_to_import": (
                        datetime.now() - datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    ).total_seconds(),
                    "metadata": run,
                }
            )
            inserted_runs_count += 1
        except DuplicateKeyError:
            logger.warning("%s already imported", run_uid)
    logger.info("%d runs inserted into MongoDB", inserted_runs_count)

    if new_runs:
        PIKA_WRAPPER.publish("repositories", {"repo_name": repo["_id"]})


def main():
    """
    Entrypoint function
    """
    mongo_filter = {"selected": True}

    # Ensure RabbitMQ queue exists
    PIKA_WRAPPER.channel.queue_declare(queue="repositories", durable=True)

    while True:
        # Copy repositories to a list as MongoDB cursor can expire if scraping is long
        LOGGER.info("Fetching repositories from MongoDB...")
        repositories = list(MONGO_REPOSITORIES.find(mongo_filter, sort=[("_id", 1)]))
        assert repositories, "Query returned no result!"
        for repo in tqdm(repositories):
            try:
                process_repo(repo)
            except Exception:
                LOGGER.exception("Fail to process repo '%s'", repo["_id"])


if __name__ == "__main__":
    main()
