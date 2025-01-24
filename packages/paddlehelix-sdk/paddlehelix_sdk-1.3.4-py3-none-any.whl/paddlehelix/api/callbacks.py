"""
定义通用的回调函数
"""

import os.path
import time

from paddlehelix.cli.client import APIClient
from paddlehelix.api.config import (DEFAULT_POLLING_INTERVAL_SECONDS,
                          ApiTaskStatusDoing, ApiTaskStatusSucc, ApiTaskStatusSubmitFailed, ApiTaskStatusCancel,
                          ApiTaskStatusFailed, ApiTaskStatusUnknown, STATUS_TO_STR)
from paddlehelix.api.task import TaskExecuteResultUtil
from paddlehelix.api.code import ErrorCode
from paddlehelix.utils import file_util

def download_task_result(save_dir: str, task_id: int, download_url) -> str:
    """
    Downloads the task result.

    Args:
        save_dir (str): The directory to save the result.
        task_id (int): The ID of the task.
        download_url (str): The URL to download the result.

    Returns:
        str: The directory where the result is saved.
    """
    try:
        file_util.create_directories(save_dir)
    except RuntimeError:
        return ""

    file_util.clear_dir(save_dir)
    if len(download_url) > 0:
        file_util.download_file(save_dir, file_util.parse_filename_from_url(download_url), download_url)
    return save_dir


class Callbacks:
    @staticmethod
    def polling_tasks(kwargs):
        execute_results = kwargs.get("execute_results", [])
        log_to_console = kwargs.get("log_to_console", True)
        if len(execute_results) <= 0:
            return
        if log_to_console:
            print("======== start to polling tasks status ========")
        task_ids = []
        for result in execute_results:
            if result.status == ApiTaskStatusDoing:
                task_ids.append(result.task_id)
        resp = APIClient.Common.query_task_infos(task_ids=task_ids)
        while True:
            running_tasks_count = 0
            for i, (tid, r) in enumerate(zip(task_ids, resp)):
                if r.code == ErrorCode.SUCCESS.value:
                    kwargs['execute_results'][i].download_url = r.data.get_download_url()
                    result = TaskExecuteResultUtil.find_result_by_task_id(tid, execute_results)
                    if r.data.status != ApiTaskStatusDoing:
                        result.status = r.data.status
                        result.execute_fail_reason = ""  # todo lilong19   (to add the task execute failure reason)
                        TaskExecuteResultUtil.store_task_execute_result(result.result_file_path, result)
                        continue
                    else:
                        running_tasks_count += 1
            if running_tasks_count <= 0:
                break
            if log_to_console:
                print(f"task is running, total count: {len(execute_results)}, "
                      f"running count: {running_tasks_count} ...")
            time.sleep(DEFAULT_POLLING_INTERVAL_SECONDS)
            resp = APIClient.Common.query_task_infos(task_ids=task_ids)
        if log_to_console:
            success_tasks, fail_tasks, cancel_tasks, submit_fail_task, doing_tasks, unknown_tasks = [], [], [], [], [], []
            for result in execute_results:
                if result.status == ApiTaskStatusSucc:
                    success_tasks.append(result.mark)
                elif result.status == ApiTaskStatusFailed:
                    fail_tasks.append(result.mark)
                elif result.status == ApiTaskStatusCancel:
                    cancel_tasks.append(result.mark)
                elif result.status == ApiTaskStatusSubmitFailed:
                    submit_fail_task.append(result.mark)
                elif result.status == ApiTaskStatusDoing:
                    doing_tasks.append(result.mark)
                else:
                    unknown_tasks.append(result.mark)
            print(f"{STATUS_TO_STR.get(ApiTaskStatusSucc)} -> Tasks ({success_tasks})")
            print(f"{STATUS_TO_STR.get(ApiTaskStatusFailed)} -> Tasks ({fail_tasks})")
            print(f"{STATUS_TO_STR.get(ApiTaskStatusCancel)} -> Tasks ({cancel_tasks})")
            print(f"{STATUS_TO_STR.get(ApiTaskStatusSubmitFailed)} -> Tasks ({submit_fail_task})")
            print(f"{STATUS_TO_STR.get(ApiTaskStatusDoing)} -> Tasks ({doing_tasks})")
            print(f"{STATUS_TO_STR.get(ApiTaskStatusUnknown)} -> Tasks ({unknown_tasks})")
        if log_to_console:
            print("======== polling tasks status finish ========")

    @staticmethod
    def download_tasks(kwargs):
        execute_results = kwargs.get("execute_results", [])
        log_to_console = kwargs.get("log_to_console", True)
        data_parent_dir = kwargs.get("data_dir")
        if log_to_console:
            print("======== start to download tasks execute results ========")
        for result in execute_results:
            if result.status == ApiTaskStatusSucc:
                if os.path.exists(result.data_dir) and not file_util.is_empty_dir(result.data_dir):
                    if log_to_console:
                        print(f"task {result.mark} already downloaded, data file path: {result.data_dir}")
                    continue
                data_dir = os.path.join(data_parent_dir, result.mark)
                download_task_result(data_dir, result.task_id, download_url=result.download_url)
                result.data_dir = data_dir
                TaskExecuteResultUtil.store_task_execute_result(result.result_file_path, result)
                print(f"task {result.mark} success download, data file path: {result.data_dir}")
        if log_to_console:
            print("======== download tasks execute results finish ========")

    @staticmethod
    def print_task_execute_results(kwargs):
        execute_results = kwargs.get("execute_results", [])
        print("======== start to print task execute results ========")
        for result in execute_results:
            print("task -> ", result.mark)
            print(result)
        print("======== print task execute results finish ========")


