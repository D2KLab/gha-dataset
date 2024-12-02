"""
Wrapper around Github API
"""

import logging
import random
import time
from datetime import datetime, timedelta
from itertools import groupby
from typing import Dict, List, Optional, Tuple, Union

import requests
import yaml

LOGGER = logging.getLogger(__name__)


class TooManyResults(Exception):
    """
    Exception raised when there is more than 1000 results
    """

    def __init__(self, message, total_count):
        super().__init__(message)
        self.total_count = total_count


class GithubApi:
    """
    Wrapper around Github API

    There is a maximum of 1,000 results even when using pagination
    """

    API_BASE_URL = "https://api.github.com/"
    MAX_ATTEMPTS = 5

    def __init__(self, config_path: str = "secrets/github_thomas.yaml") -> None:
        """
        Etags (for conditional requests) are PER-TOKEN: 2 tokens for the same request will have different Etags!
        Therefore, use a dedicated config_path for fetcher!
        """
        with open(config_path, "rt", encoding="utf-8") as fd:
            config = yaml.safe_load(fd)

        self.tokens: List[str] = config["tokens"]
        assert self.tokens, "No token provided: this is not supported"
        LOGGER.debug("%d tokens found", len(self.tokens))
        self.current_token = random.choice(self.tokens)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.current_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        # key is token, value is epoch when the token will be available again
        self.tokens_rate_limit_expiration: Dict[str, int] = {}

        # Check tokens
        self.check_tokens()


    def check_tokens(self) -> None:
        """
        Check tokens rate limit
        """
        for i, token in enumerate(self.tokens, start=1):
            self.current_token = token
            self.session.headers.update({"Authorization": f"token {self.current_token}"})
            req = self.get(url=GithubApi.API_BASE_URL + "rate_limit")
            response = req.json()
            LOGGER.info(
                "Token %d: %d/%d remaining (reset: %s)",
                i,
                int(response["resources"]["core"]["remaining"]),
                int(response["resources"]["core"]["limit"]),
                datetime.fromtimestamp(int(response["resources"]["core"]["reset"])).isoformat(),
            )
            if int(response["resources"]["core"]["remaining"]) == 0:
                self.tokens_rate_limit_expiration[self.current_token] = int(response["resources"]["core"]["reset"])


    def token_available(self) -> bool:
        """
        Check if a token is available
        """
        for token in self.tokens:
            token_ts = self.tokens_rate_limit_expiration.get(token)
            if token_ts is None:
                return True
            if token_ts < datetime.utcnow().timestamp():
                return True
        return False


    def next_token(self) -> None:
        """
        Use another token or wait until one token is available again if all tokens are rate limited
        """
        while True:
            candidates = []
            for token in self.tokens:
                token_ts = self.tokens_rate_limit_expiration.get(token)
                if token_ts is None:  # Not rate limited
                    candidates.append(token)
                    continue
                if token_ts < datetime.utcnow().timestamp():
                    candidates.append(token)
                    continue
            if candidates:
                next_token = random.choice(
                    candidates
                )  # Randomly choose 1 token among available tokens (useful when multiple workers use the same set of tokens)
                break
            LOGGER.warning(
                "No token available: next token available at %s",
                datetime.fromtimestamp(min(self.tokens_rate_limit_expiration.values())).isoformat(),
            )
            time.sleep(5)
        self.current_token = next_token
        self.session.headers.update({"Authorization": f"token {self.current_token}"})

    def get(self, url, params=None, headers=None, **kwargs):
        """
        Wrapper for GET
        """
        for _ in range(self.MAX_ATTEMPTS):
            try:
                req = self.session.get(url=url, params=params, headers=headers, **kwargs)
                # LOGGER.info("headers: %s", req.headers.items())
                if int(req.headers.get('X-RateLimit-Remaining', "5000")) < 50:
                    # We proactively use another token to avoid reaching the rate limit
                    LOGGER.debug("Less than 50 API calls with this token, using another token now to avoid being rate-limited")
                    self.next_token()
            except requests.exceptions.RequestException as exception:
                LOGGER.warning("Exception raised: %s", exception)
                continue
            if req.ok:  # 2-3xx codes
                return req
            if req.status_code >= 500:  # Try again
                time.sleep(1)
                continue
            if req.headers.get("X-RateLimit-Remaining", -1) == "0":  # we are rate-limited (HTTP 403)
                LOGGER.debug("We got rate limited: using another token")
                self.tokens_rate_limit_expiration[self.current_token] = int(req.headers["X-RateLimit-Reset"])
                self.next_token()
                continue
            if req.status_code >= 400:  # HTTP 4xx: that will probably not work even with other attempts
                LOGGER.warning("Got HTTP %d: %s", req.status_code, req.text)
                raise ValueError(f"Got HTTP {req.status_code}")
        raise IOError(f"Fail after {self.MAX_ATTEMPTS} attempts (HTTP {req.status_code})")

    def get_pages(
        self,
        url: str,
        params: Dict[str, Union[str, int, float]],
        strict: bool = True,
        list_key: str = "items",
        limit: int = None,
    ):
        """
        Github API is paginated: loop over pages
        strict: raise an exception if there is more than 1000 results (as they cannot be all retrieved)
        """
        counter = 0
        req = self.get(url=url, params=params)
        req_json = req.json()
        total_count = req_json.get("total_count", -1)  # -1 if not present
        if strict and total_count > 1000:
            raise TooManyResults(
                f"{total_count} > 1000 items returned: results will be incomplete",
                total_count,
            )

        if list_key not in req_json:
            raise ValueError(f"{list_key} not in {req_json.keys()}")
        for item in req_json[list_key]:
            counter += 1
            yield item
        while "next" in req.links:
            LOGGER.debug("%d over %d", counter, total_count)
            req = self.get(url=req.links["next"]["url"])
            for item in req.json()[list_key]:
                if limit and counter >= limit:
                    return
                counter += 1
                yield item
        if counter < total_count:
            LOGGER.warning(
                "%d items returned over %d: try to narrow down the set of results",
                counter,
                total_count,
            )

    def check_new_runs(self, full_name: str, etag: str) -> Tuple[Optional[bool], str]:
        """
        Check for new runs using Etag
        Return: (True if new runs, else False), Etag

        If etag parameter is None, first element is None.
        Second element is always the etag returned by the API.
        """
        req = self.get(
            url=GithubApi.API_BASE_URL + f"repos/{full_name}/actions/runs",
            params={
                "status": "completed",
                "per_page": 1,  # 1 element is faster to return than 100
            },
            headers={"If-None-Match": etag} if etag else {},
        )
        LOGGER.debug("response: %s", req)
        if etag:
            return req.status_code != 304, req.headers.get("Etag")  # 304 Not Modified if Etag matches
        return None, req.headers.get("Etag")

    def get_workflow_runs(
        self,
        full_name: str,
        status: str = "completed",
        to_date: datetime = None,
        from_date: datetime = None,
        limit: int = None,
        group_by_workflow: bool = True,
    ):
        """
        Get workflow runs using GH API
        from_date can be used to fetch only builds that are not already scraped.
        If not defined, from_date will be equal to 90d ago (as logs are kept 90d by default).
        """

        if not from_date:
            from_date = datetime.now() - timedelta(days=90)

        if to_date and from_date:
            created_query = "{}..{}".format(
                from_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                to_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            )
        else:
            created_query = ">{}".format(from_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"))

        runs = []
        try:
            runs.extend(
                self.get_pages(
                    GithubApi.API_BASE_URL + f"repos/{full_name}/actions/runs",
                    params={
                        "status": status,
                        "created": created_query,
                        "per_page": 100,
                    },
                    list_key="workflow_runs",
                    limit=limit,
                )
            )
        except TooManyResults as err:
            periods = (
                int(err.total_count / 800) + 1
            )  # Runs might not be equally distributed, so we take a 25% margin to try to avoid further splitting (API calls are costly)

            LOGGER.info(
                "%d results found: splitting time range into %d chunks",
                err.total_count,
                periods,
            )

            for i in range(1, 1000):  # Runs might not be uniformly distributed, so we might have to split again
                for _from_date, _to_date in self.split_time_range(from_date, to_date, periods):
                    try:
                        LOGGER.debug("Fetching runs from %s to %s...", _from_date, _to_date)
                        _runs = self.get_workflow_runs(
                            full_name,
                            status,
                            _to_date,
                            _from_date,
                            group_by_workflow=False,
                        )
                        LOGGER.debug("%d runs found", len(_runs))
                        runs.extend(_runs)
                    except TooManyResults as _err:
                        LOGGER.debug(
                            "Still to many results (%d), splitting into smaller chunks... (periods %d -> %d)",
                            _err.total_count,
                            periods,
                            periods + 1,
                        )
                        runs = []
                        periods += 1
                        break
                    if limit and len(runs) > limit:
                        break
                if runs:
                    break
                if i >= 999:
                    LOGGER.error("The maximum recursion 1000 has been exhausted, exiting the loop...")
                    break

        # Remove duplicates as API might return duplicates when using pagination (Hello GH)
        runs = list({run["id"]: run for run in runs}.values())

        runs = sorted(runs, key=lambda run: (run["path"], run["run_number"], run["run_attempt"]))

        if group_by_workflow:
            # runs list must be sorted
            return {k: list(v) for k, v in groupby(runs, key=lambda run: run["path"])}

        return runs

    @staticmethod
    def split_time_range(from_date: datetime, to_date: datetime, periods: int):
        """
        Split a date range into periods
        """
        if not to_date:
            to_date = datetime.now()
        k, m = divmod((to_date - from_date).total_seconds(), periods)
        ranges = [
            [
                from_date + timedelta(seconds=i * k + min(i, m)),
                from_date + timedelta(seconds=(i + 1) * k + min(i + 1, m)),
            ]
            for i in range(periods)
        ]
        LOGGER.info(
            "Splitting %s to %s into %d periods: %s",
            from_date,
            to_date,
            periods,
            ", ".join([f"{edges[0]} -> {edges[1]}" for edges in ranges]),
        )
        return ranges

    def get_logs(self, logs_url: str, max_size: int = 20*10**6) -> bytes:
        """
        Get step logs (ZIP archive)
        Exception will be raised by self.get on HTTP 4xx
        """
        start_time = time.time()
        req = self.get(url=logs_url, stream=True)
        content = b''
        content_size = 0
        for chunk in req.iter_content(chunk_size=16384):
            content_size += len(chunk)
            if content_size > max_size:
                LOGGER.warning("Logs archive is too big: aborting download")
                raise IOError("Logs archive is too big")
            content += chunk
        download_duration_ms = (time.time() - start_time) * 1000
        LOGGER.debug(
            "Logs archive of %0.2fMB downloaded in %dms (%0.2fMB/s)",
            content_size / 1024**2,
            download_duration_ms,
            content_size / 1024**2 / (download_duration_ms / 1000),
            extra={"logs_url": logs_url, "duration_ms": download_duration_ms, "size": content_size},
        )
        return content

    def get_diff(self, full_name, base, head):
        """
        Get code diff between commits
        """
        LOGGER.debug("Getting diff between %s and %s for %s", base, head, full_name)
        modified_files = []
        try:
            for file in self.get(
                url=GithubApi.API_BASE_URL + f"repos/{full_name}/compare/{base}..{head}",
            ).json()["files"]:
                modified_files.append(
                    {
                        "filename": file["filename"],
                        "status": file["status"],
                        "patch": file["patch"],
                    }
                )
        except ValueError:  # HTTP 4xx
            LOGGER.error("Fail to fetch diff")
            return None
        return modified_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    api = GithubApi(config_path="secrets/github.yaml")
    api.get_logs("https://api.github.com/repos/Sequel-Ace/Sequel-Ace/actions/runs/6077707540/logs")
