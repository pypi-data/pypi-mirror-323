"""
helixfold3 任务端到端执行
"""

import os.path
import threading
from time import sleep
from typing import Any

from paddlehelix.api.code import ErrorCode
from paddlehelix.api.config import (DEFAULT_TASK_COUNT_ONE_BATCH, DEFAULT_SUBMIT_INTERVAL,
                                    ApiTaskStatusSubmitFailed, ApiTaskStatusDoing, ApiTaskStatusUnknown)
from paddlehelix.api.task import Task, TaskUtil, TaskExecuteResultUtil
from paddlehelix.cli.client import APIClient
from paddlehelix.utils import file_util
from paddlehelix.version.structures import list_type, dict_type
from paddlehelix.api.callbacks import Callbacks


def execute_callbacks(**kwargs):
    callbacks = kwargs.get("callbacks", [])
    if callbacks is None or len(callbacks) <= 0:
        return
    for callback in callbacks:
        if callback is not None and callable(callback):
            callback(kwargs)


def execute_batch(task_list: list_type[Task], **kwargs) -> None:
    result_dir = kwargs.get("result_dir")
    execute_results = kwargs.get("execute_results", [])
    ready_submit_task_list, results, result_file_paths = [], [], []
    is_last_task = False
    for idx, task in enumerate(task_list):
        if task is None or task.data is None or len(task.data) <= 0:
            continue
        hash_file_name = file_util.dict_to_unique_filename(task.data)
        file_name = task.job_name + '_' + hash_file_name[:5] + '.json'
        result_file_path = os.path.join(result_dir, file_name)
        file_util.create_file_if_not_exists(result_file_path)
        result = TaskExecuteResultUtil.load_task_execute_result(result_file_path)
        if result.status != ApiTaskStatusUnknown and result.status != ApiTaskStatusSubmitFailed:
            if not kwargs.get("overwrite", False):
                print(f"The task {result.task_id} will continue polling the execution results "
                      f"based on historical submission records. If you need to overwrite, "
                      f"please set the parameter overwrite=True.")
                execute_results.append(result)
                if idx < len(task_list) - 1:
                    continue
                is_last_task = True
        if not is_last_task:
            file_util.clean_file(result_file_path)
            if len(result.data_dir) > 0:
                file_util.delete_dir_if_exist(result.data_dir)
            result = TaskExecuteResultUtil.load_task_execute_result(result_file_path)
            ready_submit_task_list.append(task)
            results.append(result)
            result_file_paths.append(result_file_path)
        if len(ready_submit_task_list) >= DEFAULT_TASK_COUNT_ONE_BATCH or idx >= len(task_list) - 1:
            # batch submit task
            resp = APIClient.MiddleHelixFold.batch_submit(data=[ready_task.data for ready_task in ready_submit_task_list])

            if not resp.success:
                for t, result, result_file_path in zip(ready_submit_task_list, results, result_file_paths):
                    result.mark, result.status, result.submit_fail_reason, result.result_file_path = (
                        t.dumps(), ApiTaskStatusSubmitFailed, resp.error_message, result_file_path)
                    TaskExecuteResultUtil.store_task_execute_result(result_file_path, result)
                    execute_results.append(result)
                continue
            task_ids = resp.data.data.task_ids
            for task_id, t, result, result_file_path in zip(task_ids, ready_submit_task_list, results,
                                                            result_file_paths):
                if task_id > 0:
                    result.task_id, result.mark, result.status, result.result_file_path = (
                        task_id, t.dumps(), ApiTaskStatusDoing, result_file_path)
                    TaskExecuteResultUtil.store_task_execute_result(result_file_path, result)
                    execute_results.append(result)
                else:
                    result.mark, result.status, result.submit_fail_reason, result.result_file_path = (
                        t.dumps(), ApiTaskStatusSubmitFailed, resp.error_message, result_file_path)
                    TaskExecuteResultUtil.store_task_execute_result(result_file_path, result)
                    execute_results.append(result)
            task_names = [task.job_name for task in ready_submit_task_list]
            print(f"batch submit task: {task_names}")
            sleep(DEFAULT_SUBMIT_INTERVAL)
            ready_submit_task_list, results, result_file_paths = [], [], []
    kwargs["execute_results"] = execute_results
    thread = threading.Thread(target=execute_callbacks, kwargs=kwargs)
    thread.start()
    if kwargs.get("block", True):
        thread.join()


def execute(data: dict_type[str, Any] = None, data_list: list_type[dict_type[str, Any]] = None, **kwargs) -> None:
    """
    HelixFold3任务端到端执行

    Args:
        data (dict): 请求的数据对象。
        data_list (list): 请求的数据对象列表。
        output_dir (str): 任务输出目录。

    Returns:
        None
    """
    # parse task data
    output_dir = kwargs.get("output_dir", "")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    data_dir, result_dir = os.path.join(output_dir, "data"), os.path.join(output_dir, "result")
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)
    kwargs["data_dir"], kwargs["result_dir"] = data_dir, result_dir
    task_list = TaskUtil.parse_task_data_list_from_all_kinds_input(data, data_list, **kwargs)

    # submit tasks
    kwargs["execute_results"] = []

    # set callbacks
    callbacks = kwargs.get("callbacks", [])
    callbacks.insert(0, Callbacks.print_task_execute_results)
    callbacks.insert(0, Callbacks.download_tasks)
    callbacks.insert(0, Callbacks.polling_tasks)
    kwargs["callbacks"] = callbacks
    execute_batch(task_list, **kwargs)
