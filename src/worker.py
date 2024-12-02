"""
Proccess repositories from RabbitMQ queue
"""

import hashlib
import io
import json
import logging
import gzip
import zlib
import os
import pika
import pathlib
import re
import tarfile
import time
import zipfile
from datetime import datetime, timedelta
from itertools import groupby

import pymongo
from pythonjsonlogger import jsonlogger

from src.api.github import GithubApi
from src.logs.parser import parse_log
from src.tools.mq import PikaWrapper

# Setup logging
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.INFO,
)

if os.environ.get("JSON_LOGS") == "true":
    json_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s")
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(json_formatter)
    logging.getLogger().handlers.clear()
    logging.getLogger().addHandler(log_handler)

LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG if os.environ.get("DEBUG", "false") == "true" else logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)


# Global variables

MONGO_CLIENT = pymongo.MongoClient(
    host=os.environ.get("MONGODB_HOST", "127.0.0.1"),
    port=int(os.environ.get("MONGODB_PORT", "27017")),
)
MONGO_REPOSITORIES = MONGO_CLIENT["gha-scraper"]["repositories"]
MONGO_RUNS = MONGO_CLIENT["gha-scraper"]["runs"]

GITHUB_API = GithubApi()

DATA_DIR = os.environ.get("DATA_DIR", "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

SANITIZE_PATTERN = re.compile(r"[^0-9a-zA-Z]+")

JOB_LOG_PATH = re.compile(r"^[^/]*\.txt$")  # .txt files in root folder (jobs)

SHELL_COMMAND_SEPARATOR = re.compile(r".*(&&|\|\||;|\||&|[^\\]\n).*")


def sanitize_string(text: str) -> str:
    """
    Remove non-alphanumeric characters from string while preserving uniqueness
    """
    return f"{SANITIZE_PATTERN.sub('_', text)}_{hashlib.sha256(text.encode()).hexdigest()[:4]}"


def get_run_log(run_metadata):
    """
    Store log on filesystem
    Convert from ZIP archive to tar.gz as ZIP is compressing files independently!
    """
    if datetime.now() - datetime.strptime(run_metadata["created_at"], "%Y-%m-%dT%H:%M:%SZ") > timedelta(days=90):
        LOGGER.warning("Run ran more than 90d ago: log was likely deleted")
        raise ValueError("More than 90d old")

    zip_bytes = GITHUB_API.get_logs(run_metadata["logs_url"])

    # Compute log archive path
    workflow_log_dir = os.path.join(
        LOGS_DIR,
        run_metadata["repository"]["full_name"],
        sanitize_string(run_metadata["name"]),
    )
    pathlib.Path(workflow_log_dir).mkdir(parents=True, exist_ok=True)

    logs_archive = os.path.join(
        workflow_log_dir,
        f"{run_metadata['run_number']}-{run_metadata['run_attempt']}.tar.gz",
    )

    # Copy logs from ZIP to tar archive
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_fd, tarfile.open(logs_archive, "w:gz") as tar_fd:
        for zip_info in zip_fd.infolist():
            tar_info = tarfile.TarInfo(name=zip_info.filename)
            tar_info.size = zip_info.file_size
            tar_info.mtime = time.mktime(tuple(zip_info.date_time) +(-1, -1, -1))
            tar_fd.addfile(
                tarinfo=tar_info,
                fileobj=zip_fd.open(zip_info.filename)
            )

    LOGGER.info("Logs saved to %s", logs_archive)

    return logs_archive


def parse_run(run):
    """
    Parse run (compute log_insights)
    """
    log_insights = []
    total_logs_size = 0
    with tarfile.open(run["logs_archive"]["path"], "r:gz") as archive_fd:
        for member in archive_fd.getmembers():
            if not JOB_LOG_PATH.match(member.name):
                continue

            # If the job was already parsed, reuse results
            if run.get("log_insights", []):
                parsed_job = next((job for job in run["log_insights"] if job["file"] == member.name), {})

                force_reparse = False
                for step in parsed_job.get("steps", []):
                    if step ["type"] == "shell" and step.get("commands"):
                        if len(step["commands"]) == 1 and SHELL_COMMAND_SEPARATOR.match(step.get("code", "")):
                            LOGGER.debug("Force reparse because there is only 1 command but there are shell separators")
                            force_reparse = True
                            break

                        commands = [command.get("command") for command in step["commands"]]
                        if "npm" in commands:
                            LOGGER.debug("Force reparse because there is tar command")
                            force_reparse = True
                            break

                if parsed_job and not parsed_job.get("error") and not force_reparse:
                    LOGGER.debug("Job %s already parsed: reusing results", member.name)
                    log_insights.append(parsed_job)
                    total_logs_size += parsed_job["log_size"]
                    continue

            total_logs_size += member.size
            LOGGER.debug("Log size: %0.2f", member.size/10**6)
            if member.size/10**6 > 100:
                LOGGER.warning("Log too large: ignored")
                log_insights.append(
                    {
                        "file": member.name,
                        "log_size": member.size,
                        "error": "Log too large"
                    }
                )
                continue
            try:
                start_time = time.time()
                parsing_results = parse_log(archive_fd.extractfile(member).read().decode("utf-8"))
                parsing_duration_ms = (time.time() - start_time) * 1000
                LOGGER.info(
                    "Log parsed in %dms",
                    parsing_duration_ms,
                    extra={"duration_ms": parsing_duration_ms}
                )
            except Exception as err:
                LOGGER.exception("Fail to parse log '%s'", member.name)
                raise err
            if parsing_results.get("steps"):
                log_insights.append(
                    {
                        "file": member.name,
                        **parsing_results
                    }
                )
    try:
        MONGO_RUNS.update_one(
            {"_id": run["_id"]},
            {"$set":
                {
                    "log_insights": log_insights,
                    "total_logs_size": total_logs_size
                }
            }
        )
    except Exception as err:
        LOGGER.exception("Fail to update run '%s'", run["_id"])
        raise err
    LOGGER.info("%d jobs parsed with success", len(log_insights))   


def delete_run(run):
    """
    Delete log archive and logs insights
    """
    logs_archive_path = run.get("logs_archive", {}).get("path")
    if logs_archive_path and os.path.isfile(logs_archive_path):
        LOGGER.info("Deleting %s", logs_archive_path)
        os.remove(logs_archive_path)
    MONGO_RUNS.delete_one({"_id": run["_id"]})


def download_run_log(run):
    """
    Download log archive
    """
    try:
        run["logs_archive"] = {"path": get_run_log(run["metadata"])}
    except Exception as exception:
        LOGGER.warning("Fail to download log '%s': %s", run["metadata"]["logs_url"], str(exception))
        run["logs_archive"] = {"error": str(exception)}
    MONGO_RUNS.update_one({"_id": run["_id"]}, {"$set": {"logs_archive": run["logs_archive"]}})
    return run


def process_repo(repo_name: str) -> bool:
    """
    Process repo
    """

    LOGGER.info("Processing %s...", repo_name)

    runs = list(
        MONGO_RUNS.find(
            {"repository_name": repo_name},
            sort=[("workflow_path", 1), ("metadata.created_at", 1)],
        )
    )
    runs_by_workflows = {k: list(v) for k, v in groupby(runs, key=lambda run: run["workflow_path"])}

    ### We want the 5 most recent runs for each workflow
    nb_runs = 0
    for workflow_path, workflow_runs in runs_by_workflows.items():

        runs_to_process = workflow_runs[-5:]  # 5 most recents runs
        nb_runs += len(runs_to_process)

        runs_to_delete = workflow_runs[:-5]
        for run in runs_to_delete:
            delete_run(run)
        LOGGER.info("%d runs deleted", len(runs_to_delete), extra={"repo_name": repo_name, "workflow_path": workflow_path})

        LOGGER.info("%d runs to process", len(runs_to_process), extra={"repo_name": repo_name, "workflow_path": workflow_path})
        for run in runs_to_process:
            if (not run.get("logs_archive", {}).get("path") and not run.get("logs_archive", {}).get("error")) \
                 or (run.get("logs_archive", {}).get("path") and not os.path.isfile(run.get("logs_archive", {}).get("path"))) \
                 and GITHUB_API.token_available():  # Ignore if no token available
                run = download_run_log(run)

            if run.get("logs_archive", {}).get("path"):  # Download can fail, thus we check again for logs_archive.path
                try:
                    parse_run(run)
                except (gzip.BadGzipFile, zlib.error):
                    LOGGER.exception("Fail to parse run '%s'", run["_id"])
                    LOGGER.warning("Deleting %s because it is corrupted", run["logs_archive"]["path"])
                    os.remove(run["logs_archive"]["path"])  # If file is corrupted, delete it
                    MONGO_RUNS.update_one({"_id": run["_id"]}, {"$unset": {"logs_archive": ""}})

    MONGO_REPOSITORIES.update_one(
        {"_id": repo_name},
        {
            "$set": {
                "processed": True,
                "nb_workflows": len(runs_by_workflows),
                "nb_runs": nb_runs
            }
        }
    )

    return True


def on_message(channel, method_frame, _, body):
    """
    Callback function on RabbitMQ message
    """

    mq_message = json.loads(body.decode())
    LOGGER.info("Received RabbitMQ message: %s", mq_message, extra={"repo_name": mq_message["repo_name"]})

    try:
        success = process_repo(mq_message["repo_name"])
        LOGGER.info("Repo processed with success", extra={"repo_name": mq_message["repo_name"]})
    except Exception:
        LOGGER.exception("Fail to process repo", extra={"repo_name": mq_message["repo_name"]})
        success = False

    # On failure, requeue at the end of the queue
    if not success:
        channel.basic_publish(
            exchange="",
            routing_key="repositories",
            body=body,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    # Pod liveness is based on freshness of this file
    # with open(os.environ.get("LIVENESS_FILE", "/tmp/liveness"), "wt", encoding="utf-8") as fd:
    #     fd.write(datetime.now().isoformat())


def worker() -> None:
    """
    Loop on MQ messages
    """
    while True:
        try:
            pika_wrapper = PikaWrapper(f"worker_{os.uname().nodename}")
            pika_wrapper.channel.basic_qos(prefetch_count=1)

            pika_wrapper.channel.basic_consume("repositories", on_message)
            try:
                pika_wrapper.channel.start_consuming()
            except KeyboardInterrupt:
                pika_wrapper.channel.stop_consuming()

                requeued_messages = pika_wrapper.channel.cancel()
                LOGGER.info("Requeued %d messages", requeued_messages)

                pika_wrapper.close()

                break
        except Exception:
            LOGGER.exception("RabbitMQ failure")


def main():
    """
    Entrypoint function
    """
    # Start worker
    worker()


if __name__ == "__main__":
    main()
