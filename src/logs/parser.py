"""
This module provides log parsing capabilities
"""

import json
import logging
import os
import re
import time
import random
from datetime import datetime
from typing import Dict

import requests

LOGGER = logging.getLogger(__name__)

# API URL
BASH_PARSER_API_URL = os.environ.get("BASH_PARSER_API_URL", "http://bash-command-extractor-api")

# Session
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "text/plain"})

# Action metadata parsing
ACTIONS_DOWNLOAD = re.compile(r"^.{28} Download action repository '(?P<repo>[^/]+)/(?P<name>[^@]+)@(?P<version>[^']+)' \(SHA:(?P<sha>\w+)\)$", re.MULTILINE)

ACTION_REF = re.compile(r'^(?P<repo>[^/]+)/(?P<name>[^/@]+)/?(?P<folder>[^@]+)?@(?P<version>.+)$')

# Runner envrioment parsing
# This regular expression can extract unexpected lines (lines other than those indicating the permissions of the Github token).
# Let's see if this is the case before making the expression more complex...
TOKEN_PERMISSIONS = re.compile(r"^.{28} (?P<scope>\w+): (?P<permission>write|read)$", re.MULTILINE)
IMAGE_VERSION = re.compile(r"Runner Image\n.{28} Image: (?P<image>[\w.-]+)\n.{28} Version: (?P<version>[\w.-]+)\n")

# Step parsing
LOG_GROUPS_PATTERN = re.compile(r'(?P<start>.{28}) ##\[group\]Run (?P<target>[^\n]+)(.*?)\n.{28} ##\[endgroup\]', re.DOTALL)

# Action parameters parsing
WITH_BLOCK_PATTERN = re.compile(r'with:\n(.+?)(?:\n.{28} \w|$)', re.DOTALL)
ENV_BLOCK_PATTERN = re.compile(r'env:\n(.+?)(?:\n.{28} \w|$)', re.DOTALL)
ACTION_PARAMETERS_KEY_VALUE = re.compile(r'\s{3}(?P<key>.*):\s(?P<value>.*)')

# Shell parsing
SHELL_COMMANDS_PATTERN = re.compile(r'.{28} \[36;1m(?P<command>.*?)\[0m$', re.MULTILINE)


def parse_context(log: str) -> Dict[str, any]:
    """
    Extract actions used, token permissions and runner image from the log
    """
    info = {}

    token_permissions = TOKEN_PERMISSIONS.findall(log)
    if token_permissions:
        info["token_permissions"] = {}
        for token_permission in token_permissions:
            info["token_permissions"][token_permission[0]] = token_permission[1]

    image_version = IMAGE_VERSION.search(log)
    if image_version:
        info["image"], info["image_version"] = image_version.groups()

    return info


def parse_action_parameters(body: str) -> Dict[str, any]:
    """
    Extract dict of with: parameters
    """
    with_parameters = {}
    env_parameters = {}

    with_block = WITH_BLOCK_PATTERN.search(body)
    env_block = ENV_BLOCK_PATTERN.search(body)

    if with_block:
        with_parameters = dict(ACTION_PARAMETERS_KEY_VALUE.findall(with_block.group(1)))

    if env_block:
        env_parameters = dict(ACTION_PARAMETERS_KEY_VALUE.findall(env_block.group(1)))

    return {
        "with": with_parameters,
        "env": env_parameters,
    }


def parse_shell_parameters(body: str) -> Dict[str, any]:
    """
    Extract dict of shell parameters
    """
    shell_parameters = {
        "env": {},
        "code": "",
    }

    env_block = ENV_BLOCK_PATTERN.search(body)
    if env_block:
        shell_parameters["env"] = dict(ACTION_PARAMETERS_KEY_VALUE.findall(env_block.group(1)))

    shell_commands = SHELL_COMMANDS_PATTERN.findall(body)
    if shell_commands:
        shell_parameters["code"] = "\n".join(shell_commands)
        shell_parameters.update(run_bash_command_extractor(shell_parameters["code"]))
    else:
        LOGGER.warning("No shell command found in: %s", body)

    return shell_parameters


def run_bash_command_extractor(code: str, max_attempts: int = 3) -> Dict[str, any]:
    """
    Call bash-command-extractor API
    """
    LOGGER.debug("Shell code: %s", code)
    for i in range(1, max_attempts + 1):
        try:
            req = SESSION.post(BASH_PARSER_API_URL, data=code, timeout=10)
            if req.status_code == 500:
                LOGGER.warning("Error while parsing shell code: %s", req.text)
                return {"error": {"error": "Parser exception", "originalError": req.text}}
            if req.status_code == 400:
                LOGGER.warning("Error while parsing shell code: %s", req.text)
                return {"error": {"error": "Invalid request", "originalError": req.text}}

            result = req.json()

            if not result:
                LOGGER.warning("Empty response from parser")
                return {"error": {"error": "Empty response from parser"}}

            if result.get("originalError"):
                LOGGER.warning("Invalid shell code: %s", result["originalError"])
                return {"error": {"error": "Invalid shell code", "originalError": result["originalError"]}}
            
            return result

        except Exception as exception:
            LOGGER.exception("Fail to call bash parser")
            if i == max_attempts:
                return {"error": {"error": f"Fail to call shell parser after {max_attempts} attempts", "exception": exception}}
        time.sleep(random.random() * 2**i)


def parse_log(log: str) -> Dict[str, any]:
    """
    Parse log and return insights extracted from the log
    """

    info = {}

    info.update(
        {
            "total_lines": log.count("\n"),
            "log_size": len(log),
        }
    )

    info.update(parse_context(log))

    # Extract list of actions from "Download action repository" lines
    actions = {}
    for action in ACTIONS_DOWNLOAD.findall(log):
        actions[f"{action[0]}/{action[1]}@{action[2]}"] = (
            {
                "repository": action[0],
                "action": action[1],
                "version": action[2],
                "sha": action[3],
            }
        )
    LOGGER.debug("actions: %s", actions)

    # Loop on matched groups
    steps = []
    for start_date_str, target, body in LOG_GROUPS_PATTERN.findall(log):
        LOGGER.debug("Processing step 'Run %s'\nbody: %s", target, body)
        step_info = {}

        # For actions, run can be "Run github/codeql-action/autobuild@v2"
        # But in actions dict, it will be "github/codeql-action@v2" (as extraction from 'Download action repository' log messages)
        target_action = ACTION_REF.search(target)
        if target_action:
            step_info["type"] = "action"
            action_info = actions.get(f"{target_action.group('repo')}/{target_action.group('name')}@{target_action.group('version')}")
            if action_info:
                step_info.update(action_info)
            else:
                LOGGER.warning("No action info for %s", target_action)
                step_info.update({
                    "repository": target_action.group('repo'),
                    "action": target_action.group('name'),
                    "version": target_action.group('version')
                })
            if target_action.group('folder'):
                step_info["folder"] = target_action.group('folder')
        else:
            step_info["type"] = "shell"

        if step_info["type"] == "action":
            step_info.update(parse_action_parameters(body))
        else:
            step_info.update(parse_shell_parameters(body))

        step_info["start_date"] = datetime.strptime(start_date_str[:-2], "%Y-%m-%dT%H:%M:%S.%f")
        if steps:
            steps[-1]["duration_sec"] = (step_info["start_date"] - steps[-1]["start_date"]).total_seconds()

        LOGGER.debug("step_info: %s", step_info)

        steps.append(step_info)

    # Find the duration of the last step (if there is at least 1 step)
    if steps:
        final_line_date = datetime.strptime(log.splitlines()[-1][:26], "%Y-%m-%dT%H:%M:%S.%f")
        try:
            steps[-1]["duration_sec"] = (final_line_date - steps[-1]["start_date"]).total_seconds()
        except ValueError:
            LOGGER.warning("Fail to compute duration_sec for last step because parsing of final line failed: '%s'", final_line_date)

    info["steps"] = steps

    return info


if __name__ == "__main__":
    import hashlib
    import os
    import zipfile

    from src.api.github import GithubApi
    logging.basicConfig(level=logging.DEBUG)

    logs_url = "https://api.github.com/repos/Sequel-Ace/Sequel-Ace/actions/runs/6077707540/logs"

    tmp_file = os.path.join("/tmp", hashlib.sha1(logs_url.encode()).hexdigest() + ".zip")
    if not os.path.isfile(tmp_file):
        with open(tmp_file, "wb") as fd:
            fd.write(GithubApi().get_logs(logs_url))

    with zipfile.ZipFile(tmp_file) as zip_fd:
        for zip_info in zip_fd.infolist():
            if "/" in zip_info.filename:  # Only job logs
                continue
            with zip_fd.open(zip_info.filename) as f:
                _log = f.read().decode()
                print(json.dumps(parse_log(_log), indent=4, default=str))
                print("***")
