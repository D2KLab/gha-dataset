"""
Get runs
"""

import gzip
import json
import logging
import os
from datetime import datetime, timedelta

import pymongo
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm

from src.api.github import GithubApi

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s",
    level=logging.DEBUG if os.environ.get("DEBUG") == "true" else logging.INFO,
)

LOGGER = logging.getLogger(__name__)


REPOSITORIES_FILE = "data/repositories_shuffled.json.gz"

MONGO_CLIENT = pymongo.MongoClient(
    host=os.environ.get("MONGODB_HOST", "127.0.0.1"),
    port=int(os.environ.get("MONGODB_PORT", "27017")),
)
MONGO_REPOSITORIES = MONGO_CLIENT["gha-scraper"]["repositories"]
MONGO_RUNS = MONGO_CLIENT["gha-scraper"]["runs"]

GITHUB_API = GithubApi()


def get_repos():
    """
    Get repos from JSON lines
    """
    with gzip.open(REPOSITORIES_FILE, "rt") as fd:
        for line in fd:
            yield json.loads(line)


def process_repo(repo):
    """
    Scrape repo
    """

    if MONGO_REPOSITORIES.find_one({"_id": repo["name"]}):
        LOGGER.debug("Repository already processed: ignored")
        return
    LOGGER.info("Processing %s...", repo["name"])

    try:
        workflow_runs = GITHUB_API.get_workflow_runs(
            repo["name"], from_date=(datetime.now() - timedelta(days=90)), limit=10**4
        )
    except ValueError as err:
        LOGGER.exception("Fail to fetch %s", repo["name"])
        MONGO_REPOSITORIES.insert_one(
            {"_id": repo["name"], "total_runs_90d": -1, "scraping_error": str(err), "repo": repo}
        )
        return

    all_runs = []
    for runs in workflow_runs.values():
        all_runs.extend(runs)
    LOGGER.info("%d runs found for %s", len(all_runs), repo["name"])

    # Ensure we can download logs for this repository
    if all_runs:
        try:
            logs_url = max(all_runs, key=lambda run: run["created_at"])["logs_url"]
            GITHUB_API.get_logs(logs_url)
        except (IOError, ValueError) as err:
            LOGGER.info("Cannot fetch logs (%s) at %s: repository will be ignored", err, logs_url)
            MONGO_REPOSITORIES.insert_one(
                {"_id": repo["name"], "total_runs_90d": -1, "scraping_error": str(err), "repo": repo}
            )
            return

    for workflow_name, runs in workflow_runs.items():
        LOGGER.info("Processing workflow '%s' (%d runs)", workflow_name, len(runs))

        for run in runs:
            run_uid = f"{repo['name']}_{workflow_name}_{run['run_number']}_{run['run_attempt']}"
            try:
                MONGO_RUNS.insert_one(
                    {
                        "_id": run_uid,
                        "repository_name": repo["name"],
                        "workflow_path": workflow_name,
                        "run_number": run["run_number"],
                        "run_attempt": run["run_attempt"],
                        "metadata": run,
                    }
                )
            except DuplicateKeyError:
                LOGGER.warning("%s already scraped", run_uid)

    # Insert repo only after processing runs
    MONGO_REPOSITORIES.insert_one({"_id": repo["name"], "total_runs_90d": len(all_runs), "repo": repo})


def main():
    """
    Entrypoint function
    """
    for repo in tqdm(get_repos(), total=240781, smoothing=0.1):
        try:
            process_repo(repo)
        except Exception as err:
            LOGGER.exception("Fail to process %s", repo["name"])
            MONGO_REPOSITORIES.insert_one(
                {
                    "_id": repo["name"],
                    "total_runs_90d": -2,
                    "scraping_error": str(err),
                    "repo": repo,
                }  # -2 scraping error that should be retried
            )


if __name__ == "__main__":
    main()
