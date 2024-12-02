"""
This script allow to fetch and shuffle list of repositories with more than 100 stars.
We use seart-ghs.si.usi.ch to discover repositories.
"""

import gzip
import json
import logging

import requests
import urllib3

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# seart-ghs.si.usi.ch has an incomplete cert validation chain
# No secret info such as tokens are exchanged, so we can disable TLS validation for now
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### Variables

OUTPUT_FILE = "data/repositories.json.gz"

SEARCH_API_URL = "https://seart-ghs.si.usi.ch/api/r/search"

### End of variables

session = requests.Session()


def get_repos():
    """
    Get repos from seart-ghs.si.usi.ch
    """

    search_params = {"nameEquals": "false", "starsMin": 100}  # false = no name criterion

    req = session.get(url=SEARCH_API_URL, params={**search_params, "page": 0}, verify=False)
    req_json = req.json()

    total_items = req_json["totalItems"]
    LOGGER.info("Found %d repositories", total_items)

    for item in req_json["items"]:
        yield item

    total_pages = req_json["totalPages"]

    for page_id in range(1, total_pages):
        req = session.get(url=SEARCH_API_URL, params={**search_params, "page": page_id}, verify=False)
        req_json = req.json()
        LOGGER.info("Processing page %d over %d...", page_id, total_pages)
        for item in req_json["items"]:
            yield item


def main():
    with gzip.open(OUTPUT_FILE, "wt") as fd:
        for repo in get_repos():
            fd.write(json.dumps(repo) + "\n")

    LOGGER.info("Done")


if __name__ == "__main__":
    main()
