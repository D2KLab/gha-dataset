"""
Force reprocessing of all repos
"""

import logging
import os
import random

import pymongo
from tqdm import tqdm

from src.tools.mq import PikaWrapper

# Setup logging
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG if os.environ.get("DEBUG", "false") == "true" else logging.INFO)

MONGO_CLIENT = pymongo.MongoClient(
    host=os.environ.get("MONGODB_HOST", "127.0.0.1"),
    port=int(os.environ.get("MONGODB_PORT", "27017")),
)
MONGO_REPOSITORIES = MONGO_CLIENT["gha-scraper"]["repositories"]
MONGO_RUNS         = MONGO_CLIENT["gha-scraper"]["runs"]

PIKA_WRAPPER = PikaWrapper("force_reprocess_all_repos")


def main():
    """
    Entrypoint function
    """
    mongo_filter = {"selected": True}

    # Ensure RabbitMQ queue exists
    PIKA_WRAPPER.channel.queue_declare(queue="repositories", durable=True)

    # Reset progress flag
    LOGGER.info("Resetting processed flag to False for all repositories...")
    MONGO_REPOSITORIES.update_many(
        {"processed": True},
        {"$set": {"processed": False}}
    )

    # Copy repositories to a list as MongoDB cursor can expire if scraping is long
    LOGGER.info("Fetching repositories from MongoDB...")
    repositories = list(MONGO_REPOSITORIES.find(mongo_filter, projection={"_id": True}))
    assert repositories, "Query returned no result!"
    random.shuffle(repositories)
    for repo in tqdm(repositories):
        try:
            PIKA_WRAPPER.publish("repositories", {"repo_name": repo["_id"]})
        except Exception:
            LOGGER.exception("Fail to process repo '%s'", repo["_id"])


if __name__ == "__main__":
    main()
