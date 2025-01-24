"""
Task结构体
"""
import os.path
from typing import Any

from paddlehelix.api.config import STATUS_TO_STR, ApiTaskStatusUnknown
from paddlehelix.utils import file_util
from paddlehelix.version.structures import dict_type, list_type


class Task:
    def __init__(self, **kwargs):
        self.job_name = kwargs.get("job_name", "")
        self.filename = kwargs.get("filename", "")
        self.dir = kwargs.get("dir", "")
        self.path = kwargs.get("path", "")
        self.idx = kwargs.get("idx", -1)
        self.data = kwargs.get("data", None)

    def __str__(self):
        strs = []
        if len(self.dir) > 0:
            strs.append(self.dir)
        if len(self.filename) > 0:
            strs.append(self.filename)
        if len(self.job_name) > 0:
            strs.append(self.job_name)
        if self.idx > -1:
            strs.append(str(self.idx))
        return "_".join(strs)

    def dumps(self):
        return self.__str__()


class TaskUtil:
    @staticmethod
    def parse_task_data_list_from_file(file_path: str, file_dir: str = "") -> list_type[Task]:
        pending_data_list = []
        content_type = file_util.check_json_type(file_path)
        if content_type == 'dict':
            data = file_util.parse_json_from_file(file_path)
            pending_data_list.append(Task(job_name=data.get("job_name", ""),
                                          idx=0,
                                          data=data,
                                          filename=os.path.basename(file_path),
                                          dir=file_dir))
        elif content_type == 'list':
            data_list = file_util.parse_json_list_from_file(file_path)
            for idx, data in enumerate(data_list):
                pending_data_list.append(Task(job_name=data.get("job_name", ""),
                                              idx=idx,
                                              data=data,
                                              filename=os.path.basename(file_path),
                                              dir=file_dir))
        else:
            raise "The content format of the file indicated by the parameter file_path is invalid."
        return pending_data_list

    @staticmethod
    def parse_task_data_list_from_all_kinds_input(data: dict_type[str, Any] = None,
                                                  data_list: list_type[dict_type[str, Any]] = None,
                                                  **kwargs) -> list_type[Task]:
        pending_data_list = []
        # process the task data in 'data'
        if data is not None:
            assert isinstance(data, dict_type), "The parameter data is not of dict type."
            pending_data_list.append(Task(job_name=data.get("job_name", ""), idx=0, data=data))
        # process the task data in 'data_list'
        if data_list is not None:
            assert isinstance(data_list, list_type), "The parameter data_list is not of list type."
            for idx, data in enumerate(data_list):
                pending_data_list.append(Task(job_name=data.get("job_name", ""), idx=idx, data=data))
        # process the task data in 'file_path'
        if "file_path" in kwargs:
            file_path = kwargs.get("file_path")
            assert isinstance(file_path, str), "The parameter file_path is not of str type."
            if not os.path.isfile(file_path):
                raise "The parameter file_path cannot represent a valid file."
            data_list = TaskUtil.parse_task_data_list_from_file(file_path)
            pending_data_list += data_list
        # process the task data in 'file_dir'
        if "file_dir" in kwargs:
            file_dir = kwargs.get("file_dir")
            assert isinstance(file_dir, str), "The parameter file_dir is not of str type."
            if not os.path.isdir(file_dir):
                raise "The parameter file_dir cannot represent a valid file dir."
            file_paths = file_util.get_all_file_paths(file_dir)
            for file_path in file_paths:
                data_list = TaskUtil.parse_task_data_list_from_file(file_path, file_dir)
                pending_data_list += data_list
        return pending_data_list


class TaskExecuteResult:
    def __init__(self, **kwargs):
        # task id
        self.task_id = kwargs.get("task_id", 0)
        # task mark
        self.mark = kwargs.get("mark", "")
        # task result
        self.status = kwargs.get("status", 0)
        self.data_dir = kwargs.get("data_dir", "")
        self.result_file_path = kwargs.get("result_file_path", "")
        # fail reason
        self.submit_fail_reason = kwargs.get("submit_fail_reason", "")
        self.execute_fail_reason = kwargs.get("execute_fail_reason", "")

        self.download_url = kwargs.get("download_url", "")

    def __str__(self):
        return \
           f"""
        {{
            "task_id": {self.task_id if self.task_id > 0 else 'No task id yet.'},
            "task_mark": {self.mark},
            "submit_fail_reason": {self.submit_fail_reason},
            "status": {STATUS_TO_STR.get(self.status, STATUS_TO_STR.get(ApiTaskStatusUnknown))},
            "execute_fail_reason": {self.execute_fail_reason},
            "data_dir": {self.data_dir if len(self.data_dir) > 0 else 'No result data yet.'}
        }}\n"""

    def __dump__(self):
        return self.__str__()

    @staticmethod
    def value_of(json_content: dict_type):
        return TaskExecuteResult(**json_content)


class TaskExecuteResultUtil:
    @staticmethod
    def load_task_execute_result(result_file_path: str) -> TaskExecuteResult:
        json_content = {}
        if os.path.exists(result_file_path) and not file_util.is_file_empty(result_file_path):
            json_content = file_util.parse_json_from_file(result_file_path)
        return TaskExecuteResult.value_of(json_content)

    @staticmethod
    def store_task_execute_result(result_file_path: str, result: TaskExecuteResult) -> None:
        file_util.write_dict_to_file(result_file_path, result.__dict__)

    @staticmethod
    def find_result_by_task_id(task_id: int, results: list_type[TaskExecuteResult]) -> TaskExecuteResult:
        for result in results:
            if result.task_id == task_id:
                return result
        return TaskExecuteResult.value_of({})
