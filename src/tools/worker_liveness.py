"""
Return 0 if worker is healthy, else 1
"""

import datetime
import os
import sys

liveness_file = os.environ.get("LIVENESS_FILE", "/tmp/liveness")

with open(liveness_file, "rt", encoding="utf-8") as fd:
    last_update = datetime.datetime.fromisoformat(fd.read())
    if datetime.datetime.now() - last_update > datetime.timedelta(minutes=10):
        sys.exit(1)

sys.exit(0)
