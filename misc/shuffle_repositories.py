"""
Shuffle repositories stored in repositories.json.gz
"""

import gzip
import logging
import random

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


INPUT_FILE = "data/repositories.json.gz"
OUTPUT_FILE = "data/repositories_shuffled.json.gz"


def main():
    lines = []
    with gzip.open(INPUT_FILE, "rt") as fd:
        for line in fd:
            lines.append(line)
    LOGGER.info("JSON loaded")

    for _ in range(10):  # Why 10 times? True randomness is hard to achieve ;)
        random.shuffle(lines)
    LOGGER.info("Array shuffled")

    with gzip.open(OUTPUT_FILE, "wt") as fd:
        for line in lines:
            fd.write(line)
    LOGGER.info("JSON written")

    LOGGER.info("Done")


if __name__ == "__main__":
    main()
