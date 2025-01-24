"""
HelixFold3模型API调用
"""
from typing import Any

import requests

from paddlehelix.api.auth import APIAuthUtil
from paddlehelix.api.code import ErrorCode
from paddlehelix.api.config import HOST, SCHEME, DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, \
    MAX_CALLS_PER_PERIOD, PERIOD, DEFAULT_TIME_OUT
from paddlehelix.api.registry import ServerAPIRegistry
from paddlehelix.api.structures import Helixfold3TaskBatchSubmitResponse, Helixfold3PriceQueryResponse, ApiResponse
from paddlehelix.utils import file_util
from paddlehelix.version.structures import list_type, dict_type
from typing import Optional, Type, TypeVar, Dict, Any
from dataclasses import dataclass, fields
from .decorator import rate_limit_calls, retry_on_timeout


class BaseHelixFold3Client:
    """
    A client for interacting with the HelixFold3 API, providing methods for batch submission
    of tasks and querying task prices.

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

    def batch_submit(self, data: dict_type[str, list_type]) -> requests.Response:
        """
        Submits a batch of tasks to the HelixFold3 API.

        Args:
            data (dict_type[str, list_type]): A dictionary containing tasks to be submitted.

        Returns:
            requests.Response: The response from the HelixFold3 API.
        """
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.HelixFold3.batch_submit.uri]),
                                 headers=self.__authClient.generate_header(ServerAPIRegistry.HelixFold3.batch_submit.uri),
                                 json=data)
        return response

    def query_task_price(self, data: dict_type[str, list_type]) -> requests.Response:
        """
        Queries the price of tasks from the HelixFold3 API.

        Args:
            data (dict_type[str, list_type]): A dictionary containing tasks for which prices are queried.

        Returns:
            requests.Response: The response from the HelixFold3 API containing the task prices.
        """
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.HelixFold3.query_task_price.uri]),
                                 headers=self.__authClient.generate_header(ServerAPIRegistry.HelixFold3.query_task_price.uri),
                                 json=data)
        return response


class MiddleHelixFold3Client:
    """
    A middle-layer client for interacting with the HelixFold3 API, extending the base client
    with features such as rate-limiting, retries, and structured response parsing.

    Attributes:
        base_client (BaseHelixFold3Client): The base client used to interact with the API.
    """

    def __init__(self, ak: str = "", sk: str = ""):
        """
        Initializes the middle client with access and secret keys for authentication.

        Args:
            ak (str): Access key for API requests.
            sk (str): Secret key for API requests.
        """
        self.base_client = BaseHelixFold3Client(ak, sk)

    @rate_limit_calls(MAX_CALLS_PER_PERIOD, PERIOD)
    @retry_on_timeout(DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, DEFAULT_TIME_OUT)
    def batch_submit(self, data) -> ApiResponse[Helixfold3TaskBatchSubmitResponse]:
        """
        Submits a batch of tasks to the HelixFold3 API with additional error handling and retries.

        Args:
            data (list_type): A list of tasks to be submitted.

        Returns:
            ApiResponse[Helixfold3TaskBatchSubmitResponse]: The API response, including parsed
            data or error message.
        """
        data = {
            "tasks": data
        }
        try:
            response = self.base_client.batch_submit(data)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") != ErrorCode.SUCCESS.value:
                    return ApiResponse(success=False, error_message=resp_json.get("msg"), status_code=response.status_code)
                parsed_data = Helixfold3TaskBatchSubmitResponse.from_dict(resp_json)
                return ApiResponse(success=True, data=parsed_data)
            else:
                return ApiResponse(success=False, error_message=f"Error {response.status_code}: {response.text}", status_code=response.status_code)
        except Exception as e:
            return ApiResponse(success=False, error_message=str(e))

    @rate_limit_calls(MAX_CALLS_PER_PERIOD, PERIOD)
    @retry_on_timeout(DEFAULT_RETRY_COUNT, DEFAULT_RETRY_INTERVAL, DEFAULT_TIME_OUT)
    def query_task_price(self, data) -> ApiResponse[Helixfold3PriceQueryResponse]:
        """
        Queries the price of tasks from the HelixFold3 API with additional error handling and retries.

        Args:
            data (list_type): A list of tasks for which prices are being queried.

        Returns:
            ApiResponse[Helixfold3PriceQueryResponse]: The API response, including parsed
            task price data or error message.
        """
        data = {
            "tasks": data
        }
        try:
            response = self.base_client.query_task_price(data)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") != ErrorCode.SUCCESS.value:
                    return ApiResponse(success=False, error_message=resp_json.get("msg"), status_code=response.status_code)
                parsed_data = Helixfold3PriceQueryResponse.from_dict(resp_json)
                return ApiResponse(success=True, data=parsed_data)
            else:
                return ApiResponse(success=False, error_message=f"Error {response.status_code}: {response.text}", status_code=response.status_code)
        except Exception as e:
            return ApiResponse(success=False, error_message=str(e))
