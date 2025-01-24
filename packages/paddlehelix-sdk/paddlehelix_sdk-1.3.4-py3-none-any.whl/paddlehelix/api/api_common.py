"""
通用API调用，例如查询任务执行结果
"""
from time import sleep
from typing import Any, Dict, Type, TypeVar

from .decorator import rate_limit_calls, retry_on_timeout

T = TypeVar("T")

import requests
import time

from paddlehelix.api.auth import APIAuthUtil
from paddlehelix.api.code import ErrorCode
from paddlehelix.api.config import HOST, SCHEME, DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, MAX_CALLS_PER_PERIOD, PERIOD, \
    DEFAULT_TIME_OUT
from paddlehelix.api.config import QUERY_BATCH_NUM, QUERY_BATCH_INTERVAL
from paddlehelix.api.config import QUERY_PRICE_BATCH_DATA_NUM, QUERY_PRICE_RETRY_COUNT, QUERY_PRICE_RETRY_INTERVAL
from paddlehelix.api.registry import ServerAPIRegistry
from paddlehelix.api.structures import ApiResponse, TaskCancelResponse, TaskGetResponse
from paddlehelix.api.task import TaskUtil
from paddlehelix.utils import file_util
from paddlehelix.version.structures import list_type, dict_type
from dataclasses import dataclass, fields


class BaseCommonClient:
    """
    A client for interacting with common API endpoints.

    Attributes:
        _ak (str): Access key for authentication.
        _sk (str): Secret key for authentication.
        __authClient (APIAuthUtil): Helper class for API authentication.
    """

    def __init__(self, ak: str = "", sk: str = ""):
        """
        Initializes the client with access and secret keys for authentication.

        Args:
            ak (str): Access key for API requests.
            sk (str): Secret key for API requests.
        """
        self._ak = ak
        self._sk = sk
        self.__authClient = APIAuthUtil(ak, sk)

    def cancel_task(self, task_id: int = 0):
        """
        Cancels a task with the given task ID.

        Args:
            task_id (int): The ID of the task to be canceled. Default is 0.

        Returns:
            Response: The response from the API after attempting to cancel the task.
        """
        response = requests.post(
            "".join([SCHEME, HOST, ServerAPIRegistry.Common.cancel_task.uri]),
            headers=self.__authClient.generate_header(ServerAPIRegistry.Common.cancel_task.uri),
            json={"task_id": task_id}
        )
        return response

    def query_task_info(self, task_id: int = 0):
        """
        Queries information about a task with the given task ID.

        Args:
            task_id (int): The ID of the task to query. Default is 0.

        Returns:
            Response: The response from the API containing the task information.
        """
        response = requests.post(
            "".join([SCHEME, HOST, ServerAPIRegistry.Common.query_task_info.uri]),
            headers=self.__authClient.generate_header(ServerAPIRegistry.Common.query_task_info.uri),
            json={"task_id": task_id}
        )
        return response


class MiddleCommonClient:
    """
    A client for interacting with common API endpoints, such as canceling and
    querying tasks, with additional features like rate limiting and retry on timeout.

    Attributes:
        _ak (str): Access key for authentication.
        _sk (str): Secret key for authentication.
        base_client (BaseCommonClient): The base client used to interact with the API.
    """

    def __init__(self, ak: str = "", sk: str = ""):
        """
        Initializes the client with access and secret keys for authentication.

        Args:
            ak (str): Access key for API requests.
            sk (str): Secret key for API requests.
        """
        self._ak = ak
        self._sk = sk
        self.base_client = BaseCommonClient(ak, sk)

    @rate_limit_calls(MAX_CALLS_PER_PERIOD, PERIOD)
    @retry_on_timeout(DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, DEFAULT_TIME_OUT)
    def cancel_task(self, task_id: int = 0) -> ApiResponse[TaskCancelResponse]:
        """
        Cancels a task with the given task ID and handles rate-limiting and retries.

        Args:
            task_id (int): The ID of the task to be canceled. Default is 0.

        Returns:
            ApiResponse[TaskCancelResponse]: The response containing the status and
            result of the cancellation. If successful, contains the parsed response data.
        """
        try:
            response = self.base_client.cancel_task(task_id)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") != ErrorCode.SUCCESS.value:
                    return ApiResponse(success=False, data=None, error_message=resp_json.get("msg", ""))

                parsed_data = TaskCancelResponse.from_dict(resp_json)
                return ApiResponse(success=True, data=parsed_data)
            else:
                return ApiResponse(
                    success=False,
                    error_message=f"Error {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
        except Exception as e:
            return ApiResponse(success=False, error_message=str(e))

    @rate_limit_calls(MAX_CALLS_PER_PERIOD, PERIOD)
    @retry_on_timeout(DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, DEFAULT_TIME_OUT)
    def query_task_info(self, task_id: int = 0) -> ApiResponse[TaskGetResponse]:
        """
        Queries information about a task with the given task ID, with rate-limiting
        and retry features.

        Args:
            task_id (int): The ID of the task to query. Default is 0.

        Returns:
            ApiResponse[TaskGetResponse]: The response containing the task info.
            If successful, contains parsed task data.
        """
        try:
            response = self.base_client.query_task_info(task_id)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") != ErrorCode.SUCCESS.value:
                    return ApiResponse(success=False, data=None, error_message=resp_json.get("msg", ""))

                parsed_data = TaskGetResponse.from_dict(resp_json)
                return ApiResponse(success=True, data=parsed_data)
            else:
                return ApiResponse(
                    success=False,
                    error_message=f"Error {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
        except Exception as e:
            return ApiResponse(success=False, error_message=str(e))

    def query_task_infos(self, task_ids: list_type[int]) -> list_type[TaskGetResponse]:
        """
        Queries information about multiple tasks based on a list of task IDs.

        This method queries task information in batches, respecting rate limits.

        Args:
            task_ids (list_type[int]): A list of task IDs to query.

        Returns:
            list_type[TaskGetResponse]: A list of responses containing the task information.
        """
        task_infos = []
        for task_id in task_ids:
            response = self.query_task_info(task_id)
            task_infos.append(response.data)
            sleep(QUERY_BATCH_INTERVAL)  # To avoid hitting rate limits
        return task_infos
