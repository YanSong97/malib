# -*- encoding: utf-8 -*-
# -----
# Created Date: 2021/7/14
# Author: Hanjing Wang
# -----
# Last Modified:
# Modified By:
# -----
# Copyright (c) 2020 MARL @ SJTU
# -----

import enum
from collections import defaultdict
from functools import wraps
from malib.backend.coordinator.server import CoordinatorServer
from malib.utils.typing import TaskType, Dict
from malib.utils.errors import RegisterFailure

import cloudpickle as pkl
runtime_envs = defaultdict(lambda: [])
def task_register(target_class):
    def wrapper(function):
        global runtime_envs
        runtime_envs[target_class.__class__.__name__].append(pkl.dumps(function))
        return function
    return wrapper



RESERVED_TASK_NAMES = []


def register_task_type(tasks: Dict[str, str]):
    existing_tasks = {t.name: t.value for t in TaskType}
    for tasks_name, tasks_value in tasks.items():
        if (
            tasks_name.lower() in RESERVED_TASK_NAMES
            or tasks_name.upper() in RESERVED_TASK_NAMES
            or tasks_value.lower() in RESERVED_TASK_NAMES
            or tasks_value.upper() in RESERVED_TASK_NAMES
        ):
            raise RegisterFailure(
                f"Encountered potential conflicts "
                f"with reserved task names or value "
                f"in registering task {tasks_name}:{tasks_value}"
            )
    existing_tasks.update(tasks)
    TaskType = enum.EnumMeta("TaskType", existing_tasks)
