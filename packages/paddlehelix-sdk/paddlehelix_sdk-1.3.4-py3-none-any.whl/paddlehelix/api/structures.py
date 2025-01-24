"""
存放各种API对应的请求、响应体数据结构
"""
from dataclasses import dataclass, fields
from typing import Optional, Type, TypeVar, Dict, Any, List, Generic

import json

from paddlehelix.version.structures import list_type, dict_type

T = TypeVar("T")

class ApiResponse(Generic[T]):
    """
    A generic class to represent the API response, containing information about the success of the request,
    the data returned, any error message, and the status code.

    Attributes:
        success (bool): Indicates whether the request was successful.
        data (Optional[T]): The data returned by the API. It can be of any type.
        error_message (Optional[str]): An error message, if the request was unsuccessful.
        status_code (int): The HTTP status code returned by the API (default is 200).
    """

    def __init__(self, success: bool, data: Optional[T] = None, error_message: Optional[str] = None, status_code: int = 200):
        """
        Initializes the ApiResponse object.

        Args:
            success (bool): Whether the API request was successful.
            data (Optional[T]): The data returned from the API. Defaults to None.
            error_message (Optional[str]): An error message, if the request was unsuccessful. Defaults to None.
            status_code (int): The HTTP status code from the API. Defaults to 200.
        """
        self.success = success
        self.data = data
        self.error_message = error_message
        self.status_code = status_code

    def __repr__(self):
        """
        Returns a string representation of the ApiResponse object.

        Returns:
            str: A string representation of the ApiResponse object.
        """
        return f"ApiResponse(success={self.success}, data={self.data}, error_message={self.error_message}, status_code={self.status_code})"


@dataclass
class Data:
    """
    A data class representing the task IDs, which can be passed to API methods for batch operations.

    Attributes:
        task_ids (Optional[List[int]]): A list of task IDs to be used in batch operations.
    """

    task_ids: Optional[list_type[int]] = None

    @staticmethod
    def from_dict(d: dict) -> 'Data':
        """
        Creates a Data object from a dictionary.

        Args:
            d (dict): A dictionary containing the data.

        Returns:
            Data: A Data object created from the dictionary.
        """
        return Data(
            task_ids=d.get('task_ids')
        )


@dataclass
class Helixfold3TaskBatchSubmitResponse:
    """
    A response class representing the result of a batch task submission to the HelixFold3 API.

    The 'code' field indicates the status of the request:
        - 0: Success
        - 2001: Invalid input
        - 6001: Internal error
        - 7001: Account error
        - 8001: Request too fast
        - 8002: Failed to submit to scheduler

    Attributes:
        code (Optional[int]): The result code from the HelixFold3 API.
        data (Optional[Data]): The data related to the batch task submission (optional).
        logId (Optional[str]): The log ID for tracking the request.
        msg (Optional[str]): A message providing additional details about the result.
    """

    code: Optional[int] = None
    data: Optional[Data] = None
    logId: Optional[str] = None
    msg: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> 'Helixfold3TaskBatchSubmitResponse':
        """
        Creates a Helixfold3TaskBatchSubmitResponse object from a dictionary.

        Args:
            d (dict): A dictionary containing the response data.

        Returns:
            Helixfold3TaskBatchSubmitResponse: A response object created from the dictionary.
        """
        return Helixfold3TaskBatchSubmitResponse(
            code=d.get('code'),
            data=Data.from_dict(d.get('data')) if d.get('data') else None,
            logId=d.get('logId'),
            msg=d.get('msg')
        )

@dataclass
class TaskPriceInfo:
    """
    A data class representing the price information for a single task.

    Attributes:
        name (Optional[str]): The name of the task.
        price (Optional[float]): The price of the task.
    """

    name: Optional[str] = None
    price: Optional[float] = None

    @staticmethod
    def from_dict(d: dict) -> 'TaskPriceInfo':
        """
        Creates a TaskPriceInfo object from a dictionary.

        Args:
            d (dict): A dictionary containing the task price information.

        Returns:
            TaskPriceInfo: A TaskPriceInfo object created from the dictionary.
        """
        return TaskPriceInfo(
            name=d.get('name'),
            price=d.get('price')
        )


@dataclass
class TaskPriceInfos:
    """
    A data class representing a collection of task price information, including total price details.

    Attributes:
        discounted_total_prices (Optional[float]): The total price after any discount has been applied.
        prices (Optional[List[TaskPriceInfo]]): A list of TaskPriceInfo objects representing individual task prices.
        total_amount (Optional[float]): The total amount for all tasks without any discount.
    """

    discounted_total_prices: Optional[float] = None
    prices: Optional[List[TaskPriceInfo]] = None
    total_amount: Optional[float] = None

    @staticmethod
    def from_dict(d: dict) -> 'TaskPriceInfos':
        """
        Creates a TaskPriceInfos object from a dictionary.

        Args:
            d (dict): A dictionary containing the task price details.

        Returns:
            TaskPriceInfos: A TaskPriceInfos object created from the dictionary.
        """
        return TaskPriceInfos(
            discounted_total_prices=d.get('discounted_total_prices'),
            prices=[TaskPriceInfo.from_dict(v) for v in d.get('prices')] if d.get('prices') else None,
            total_amount=d.get('total_amount')
        )


@dataclass
class Helixfold3PriceQueryResponse:
    """
    A response class representing the result of a task price query to the HelixFold3 API.

    The 'code' field indicates the status of the request:
        - 0: Success
        - 2001: Invalid input
        - 6001: Internal error

    Attributes:
        code (Optional[int]): The result code from the HelixFold3 API.
        data (Optional[TaskPriceInfos]): The data containing task price information.
        logId (Optional[str]): The log ID for tracking the request.
        msg (Optional[str]): A message providing additional details about the result.
    """

    code: Optional[int] = None
    data: Optional[TaskPriceInfos] = None
    logId: Optional[str] = None
    msg: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> 'Helixfold3PriceQueryResponse':
        """
        Creates a Helixfold3PriceQueryResponse object from a dictionary.

        Args:
            d (dict): A dictionary containing the response data.

        Returns:
            Helixfold3PriceQueryResponse: A response object created from the dictionary.
        """
        return Helixfold3PriceQueryResponse(
            code=d.get('code'),
            data=TaskPriceInfos.from_dict(d.get('data')) if d.get('data') else None,
            logId=d.get('logId'),
            msg=d.get('msg')
        )


@dataclass
class HelixTaskInfo:
    """
    A data class representing information about a task's execution and its status.

    The 'status' field indicates the execution status:
        - 1: Success
        - 2: Running
        - -1: Failed
        - -2: Canceled

    Attributes:
        result (Optional[str]): A JSON string containing the result details, such as download URL.
        run_time (Optional[int]): The time taken for the task to run (in seconds).
        status (Optional[int]): The status of the task (1 for success, 2 for running, -1 for failure, -2 for cancellation).
    """

    result: Optional[str] = None
    run_time: Optional[int] = None
    status: Optional[int] = None

    @staticmethod
    def from_dict(d: dict) -> 'HelixTaskInfo':
        """
        Creates a HelixTaskInfo object from a dictionary.

        Args:
            d (dict): A dictionary containing the task execution information.

        Returns:
            HelixTaskInfo: A HelixTaskInfo object created from the dictionary.
        """
        return HelixTaskInfo(
            result=d.get('result'),
            run_time=d.get('run_time'),
            status=d.get('status')
        )

    def get_download_url(self) -> str:
        """
        Extracts and returns the download URL from the 'result' JSON string.

        Returns:
            str: The download URL if available; otherwise, an empty string.
        """
        if self.result is not None:
            result_dict = json.loads(self.result)
            return result_dict.get('download_url', "")
        return ""


@dataclass
class TaskGetResponse:
    """
    A response class representing the result of a task query.

    The 'code' field indicates the status of the request:
        - 0: Success
        - 2001: Invalid input
        - 1000: Internal error

    Attributes:
        code (Optional[int]): The result code from the task query.
        data (Optional[HelixTaskInfo]): The task information related to the query.
        logId (Optional[str]): The log ID for tracking the request.
        msg (Optional[str]): A message providing additional details about the result.
    """

    code: Optional[int] = None
    data: Optional[HelixTaskInfo] = None
    logId: Optional[str] = None
    msg: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> 'TaskGetResponse':
        """
        Creates a TaskGetResponse object from a dictionary.

        Args:
            d (dict): A dictionary containing the task query response data.

        Returns:
            TaskGetResponse: A response object created from the dictionary.
        """
        return TaskGetResponse(
            code=d.get('code'),
            data=HelixTaskInfo.from_dict(d.get('data')) if d.get('data') else None,
            logId=d.get('logId'),
            msg=d.get('msg')
        )


@dataclass
class TaskCancelResponse:
    """
    A response class representing the result of a task cancellation request.

    The 'code' field indicates the status of the task cancellation:
        - 0: Success
        - 2001: Invalid input
        - 1000 & 6001: Internal error
        - 8003: Task cancel failed

    Attributes:
        code (Optional[int]): The result code from the task cancellation request.
        logId (Optional[str]): The log ID for tracking the request.
        msg (Optional[str]): A message providing additional details about the cancellation result.
    """

    code: Optional[int] = None
    logId: Optional[str] = None
    msg: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> 'TaskCancelResponse':
        """
        Creates a TaskCancelResponse object from a dictionary.

        Args:
            d (dict): A dictionary containing the task cancellation response data.

        Returns:
            TaskCancelResponse: A TaskCancelResponse object created from the dictionary.
        """
        return TaskCancelResponse(
            code=d.get('code'),
            logId=d.get('logId'),
            msg=d.get('msg')
        )
