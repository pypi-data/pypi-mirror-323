"""Argos agent

Fetchs the tasks from the server, execute it and send the result to the server
"""
import asyncio
import json
import logging
import socket
from hashlib import md5
from time import sleep
from typing import List

import httpx
from tenacity import retry, wait_random  # type: ignore

from argos import VERSION
from argos.checks import get_registered_check
from argos.logging import logger
from argos.schemas import AgentResult, SerializableException, Task


def log_failure(retry_state):
    """Log failures, with a different log level depending on the number of attempts."""
    if retry_state.attempt_number < 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING
    logger.log(
        loglevel,
        "Retrying: attempt %s ended with: %s %s",
        retry_state.attempt_number,
        retry_state.outcome,
        retry_state.outcome.exception(),
    )


class ArgosAgent:  # pylint: disable-msg=too-many-instance-attributes
    """The Argos agent is responsible for running the checks and reporting the results."""

    def __init__(self, server: str, auth: str, max_tasks: int, wait_time: int):
        self.server = server
        self.max_tasks = max_tasks
        self.wait_time = wait_time
        self.auth = auth
        self._http_client: httpx.AsyncClient | None = None
        self._http_client_v4: httpx.AsyncClient | None = None
        self._http_client_v6: httpx.AsyncClient | None = None
        self._res_cache: dict[str, httpx.Response] = {}

        self.agent_id = socket.gethostname()

    @retry(after=log_failure, wait=wait_random(min=1, max=2))
    async def run(self):
        auth_header = {
            "Authorization": f"Bearer {self.auth}",
            "User-Agent": f"Argos Panoptes agent {VERSION}",
        }
        self._http_client = httpx.AsyncClient(headers=auth_header)

        ua_header = {
            "User-Agent": f"Argos Panoptes {VERSION} "
            "(about: https://argos-monitoring.framasoft.org/)",
        }
        self._http_client_v4 = httpx.AsyncClient(
            headers=ua_header,
            transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
        )
        self._http_client_v6 = httpx.AsyncClient(
            headers=ua_header, transport=httpx.AsyncHTTPTransport(local_address="::")
        )

        logger.info("Running agent against %s", self.server)
        async with self._http_client:
            while "forever":
                retry_now = await self._get_and_complete_tasks()
                if not retry_now:
                    logger.info("Waiting %i seconds before next retry", self.wait_time)
                    await asyncio.sleep(self.wait_time)

    async def _do_request(self, group: str, details: dict):
        headers = {}
        if details["request_data"] is not None:
            request_data = json.loads(details["request_data"])
            if request_data["headers"] is not None:
                headers = request_data["headers"]

        if details["ip_version"] == "4":
            http_client = self._http_client_v4
        else:
            http_client = self._http_client_v6
        try:
            if details["request_data"] is None or request_data["data"] is None:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"],
                    url=details["url"],
                    headers=headers,
                    timeout=60,
                )
            elif request_data["json"]:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"],
                    url=details["url"],
                    headers=headers,
                    json=request_data["data"],
                    timeout=60,
                )
            else:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"],
                    url=details["url"],
                    headers=headers,
                    data=request_data["data"],
                    timeout=60,
                )
        except httpx.ReadError:
            sleep(1)
            if details["request_data"] is None or request_data["data"] is None:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"], url=details["url"], timeout=60
                )
            elif request_data["json"]:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"],
                    url=details["url"],
                    json=request_data["data"],
                    timeout=60,
                )
            else:
                response = await http_client.request(  # type: ignore[union-attr]
                    method=details["method"],
                    url=details["url"],
                    data=request_data["data"],
                    timeout=60,
                )

        self._res_cache[group] = response

    async def _complete_task(self, _task: dict) -> AgentResult:
        try:
            task = Task(**_task)

            check_class = get_registered_check(task.check)
            check = check_class(task)
            result = await check.run(self._res_cache[task.task_group])
            status = result.status
            context = result.context

        except Exception as err:  # pylint: disable=broad-except
            status = "error"
            context = SerializableException.from_exception(err)
            msg = f"An exception occured when running {_task}. {err.__class__.__name__} : {err}"
            logger.error(msg)
        return AgentResult(task_id=task.id, status=status, context=context)

    async def _get_and_complete_tasks(self):
        # Fetch the list of tasks
        response = await self._http_client.get(
            f"{self.server}/api/tasks",
            params={"limit": self.max_tasks, "agent_id": self.agent_id},
        )

        if response.status_code == httpx.codes.OK:
            data = response.json()
            logger.info("Received %i tasks from the server", len(data))

            req_groups = {}
            _tasks = []
            for _task in data:
                task = Task(**_task)

                url = task.url
                group = task.task_group

                if task.check == "http-to-https":
                    data = task.request_data
                    if data is None:
                        data = ""
                    url = str(httpx.URL(task.url).copy_with(scheme="http"))
                    group = (
                        f"{task.method}-{task.ip_version}-{url}-"
                        f"{md5(data.encode()).hexdigest()}"
                    )
                    _task["task_group"] = group

                req_groups[group] = {
                    "url": url,
                    "ip_version": task.ip_version,
                    "method": task.method,
                    "request_data": task.request_data,
                }
                _tasks.append(_task)

            requests = []
            for group, details in req_groups.items():
                requests.append(self._do_request(group, details))

            if requests:
                await asyncio.gather(*requests)

            tasks = []
            for task in _tasks:
                tasks.append(self._complete_task(task))

            if tasks:
                results = await asyncio.gather(*tasks)
                await self._post_results(results)
                return True

            logger.info("Got no tasks from the server.")
            return False

        logger.error("Failed to fetch tasks: %s", response.read())
        return False

    async def _post_results(self, results: List[AgentResult]):
        data = [r.model_dump() for r in results]
        if self._http_client is not None:
            response = await self._http_client.post(
                f"{self.server}/api/results",
                params={"agent_id": self.agent_id},
                json=data,
            )

            if response.status_code == httpx.codes.CREATED:
                logger.info(
                    "Successfully posted results %s", json.dumps(response.json())
                )
            else:
                logger.error("Failed to post results: %s", response.read())
            return response

        logger.error("self._http_client is None")
