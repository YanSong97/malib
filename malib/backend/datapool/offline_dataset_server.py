import logging
import os
import sys
import traceback
import threading
import time
import traceback
import numpy as np
import torch
import ray

from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from readerwriterlock import rwlock

from ray.util import queue
from torch._C import BufferDict

from malib import settings
from malib.backend.datapool.data_array import NumpyDataArray
from malib.utils.errors import OversampleError, NoEnoughDataError, RepeatedAssignError
from malib.utils.typing import BufferDescription, PolicyID, AgentID, Status
from malib.utils.logger import get_logger, Log
from malib.utils.logger import get_logger
from malib.utils.typing import (
    BufferDescription,
    PolicyID,
    AgentID,
    Dict,
    List,
    Any,
    Type,
    Union,
    Sequence,
    Tuple,
)

import threading
import pickle as pkl


def _gen_table_name(env_id, main_id, pid):
    res = f"{env_id}"
    if main_id:
        if isinstance(main_id, List):
            main_id = "_".join(sorted(main_id))
        res += f"_{main_id}"
    if pid:
        if isinstance(pid, List):
            pid = "_".join(sorted(pid))
        res += f"_{pid}"
    return res


DATASET_TABLE_NAME_GEN = _gen_table_name
Batch = namedtuple("Batch", "identity, data")


class Episode:
    """ Unlimited buffer """

    CUR_OBS = "obs"
    NEXT_OBS = "new_obs"
    ACTION = "action"
    ACTION_MASK = "action_mask"
    REWARD = "reward"
    DONE = "done"
    ACTION_DIST = "action_prob"
    # XXX(ming): seems useless
    INFO = "infos"

    # optional
    STATE_VALUE = "state_value_estimation"
    STATE_ACTION_VALUE = "state_action_value_estimation"
    CUR_STATE = "cur_state"  # current global state
    NEXT_STATE = "next_state"  # next global state
    LAST_REWARD = "last_reward"


def iterate_recursively(d: Dict):
    for k, v in d.items():
        if isinstance(v, (dict, BufferDict)):
            yield from iterate_recursively(v)
        else:
            yield d, k, v


class BufferDict(dict):
    @property
    def capacity(self) -> int:
        capacities = []
        for _, _, v in iterate_recursively(self):
            capacities.append(v.shape[0])
        return max(capacities)

    def index(self, indices):
        return self.index_func(indices)

    def index_func(self, x, indices):
        if isinstance(x, (dict, BufferDict)):
            res = BufferDict()
            for k, v in x.items():
                res[k] = self.index_func(v, indices)
            return res
        else:
            t = x[indices]
            return t

    def set_data(self, index, new_data):
        return self.set_data_func(self, index, new_data)

    def set_data_func(self, x, index, new_data):
        if isinstance(new_data, (dict, BufferDict)):
            for nk, nv in new_data.items():
                self.set_data_func(x[nk], index, nv)
        if isinstance(new_data, torch.Tensor):
            t = new_data.cpu().numpy()
        elif isinstance(new_data, np.ndarray):
            t = new_data
        else:
            raise TypeError(
                f"Unexpected type for new insert data: {type(new_data)}, expected is np.ndarray"
            )
        x[index] = t.copy()


class Table:
    def __init__(
        self,
        keys,
        capacity: int,
        data_shapes: Dict[str, Tuple],
        sample_start_size: int = 0,
    ):
        """One table for one episode."""

        self._keys = keys
        self._threading_lock = threading.Lock()
        self._rwlock = rwlock.RWLockFairD()
        self._is_multi_agent = len(keys) > 1
        self._consumer_queue = None
        self._producer_queue = None
        self._is_fixed = False
        self._sample_start_size = sample_start_size
        self._size = 0
        self._capacity = capacity
        self._data_shapes = data_shapes

        self._consumer_queue = queue.Queue(maxsize=capacity)
        self._producer_queue = queue.Queue(maxsize=capacity)
        # ready index
        self._producer_queue.put_nowait_batch([i for i in range(capacity)])

        # build episode
        self._buffer = BufferDict()
        for k in keys:
            t = BufferDict()
            for dk, dshape in data_shapes.items():
                t[dk] = np.zeros((capacity,) + dshape)
            self._buffer[k] = t

    @property
    def is_fixed(self):
        return self._is_fixed

    @property
    def is_multi_agent(self) -> bool:
        return self._is_multi_agent

    @property
    def buffer(self) -> BufferDict:
        return self._buffer

    @property
    def size(self):
        return self._size

    @property
    def capacity(self):
        self._capacity

    def sample_activated(self) -> bool:
        return self._consumer_queue.size() >= self._sample_start_size

    def fix_table(self):
        self._is_fixed = True
        self._producer_queue.shutdown()
        self._consumer_queue.shutdown()

    def get_index(self, buffer_size: int) -> Union[List[int], None]:
        buffer_size = min(self._producer_queue.size(), buffer_size)
        if buffer_size == 0:
            return None
        else:
            return self._producer_queue.get_nowait_batch(buffer_size)

    def free_index(self, indexes: List[int]):
        self._consumer_queue.put_nowait_batch(indexes)

    @staticmethod
    def gen_table_name(*args, **kwargs):
        return DATASET_TABLE_NAME_GEN(*args, **kwargs)

    def insert(self, indexes: List[int], data: Dict[str, Any]):
        self._buffer.set_data(indexes, data)
        self._size += len(indexes)

    def sample(self, indices: List[int]) -> Dict[str, Any]:
        return self._buffer.index(indices)

    @staticmethod
    def _save_helper_func(obj, fp, candidate_name=""):
        if os.path.isdir(fp):
            try:
                os.makedirs(fp)
            except:
                pass
            tfp = os.path.join(fp, candidate_name + ".tpkl")
        else:
            paths = os.path.split(fp)[0]
            try:
                os.makedirs(paths)
            except:
                pass
            tfp = fp + ".tpkl"
        with open(tfp, "wb") as f:
            pkl.dump(obj, f, protocol=settings.PICKLE_PROTOCOL_VER)

    def dump(self, fp, name=None):
        if name is None:
            name = self._name
        with self._threading_lock:
            serial_dict = {
                "keys": self._keys,
                "data": self._buffer,
                "multi_agent": self._is_multi_agent,
                "sample_start_size": self._sample_start_size,
                "data_shapes": self._data_shapes,
            }
            self._save_helper_func(serial_dict, fp, name)

    @classmethod
    def load(cls, fp):
        with open(fp, "rb") as f:
            serial_dict = pkl.load(f)

        table = Table(
            keys=serial_dict["keys"],
            capacity=serial_dict["capacity"],
            data_shapes=serial_dict["data_shapes"],
            sample_start_size=serial_dict["sample_start_size"],
        )
        table._buffer = serial_dict["data"]
        table._capacity = table.buffer.capacity
        return table

    def to_csv(self, fp):
        def _dump_episode(fname, episode):
            class _InternelColumnGenerator:
                def __init__(self, column_data_dict):
                    self.idx = 0
                    self.data = column_data_dict
                    self.columns = list(column_data_dict.keys())
                    self.length = len(next(iter(column_data_dict.values)))

                def getline(self):
                    column_info = ",".join(self.columns)
                    yield column_info
                    while self.idx < self.length:
                        line = []
                        for c in self.columns:
                            line.append(str(self.data[c][self.idx]))
                        line = ",".join(line)
                        self.idx += 1
                        yield line

            wg = _InternelColumnGenerator(episode.data)
            with open(fname, "w") as f:
                while True:
                    line = wg.getline()
                    if line:
                        f.write(line)
                    else:
                        break

        with self._threading_lock:
            try:
                os.makedirs(fp)
            except:
                pass

            if self.multi_agent:
                for aid in self._data.keys():
                    episode = self._episode[aid]
                    _dump_episode(os.path.join(fp, aid), episode)
            else:
                _dump_episode(fp, self._episode)


class ExternalDataset:
    def __init__(self, name, path, sample_rate=0.5):
        self._name = name
        if os.path.isabs(path):
            self._path = path
        else:
            self._path = os.path.join(settings.BASE_DIR, path)
        self._sample_rate = sample_rate

    def sample(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class ExternalReadOnlyDataset(ExternalDataset):
    def __init__(
        self, name, path, sample_rate=0.5, mapping_func=lambda x: x, binary=True
    ):
        super().__init__(name, path, sample_rate=sample_rate)

        self._tables: Dict[str, Table] = {}
        for fn in os.listdir(self._path):
            if fn.endswith(".tpkl"):
                table = Table.load(os.path.join(self._path, fn))
                self._tables[table.name] = table

    def sample(self, buffer_desc: BufferDescription):
        info = f"{self._name}(external, read-only): OK"
        try:
            # NOTE(zbzhu): maybe we do not care which policy sampled the (expert) data
            table_name = Table.gen_table_name(
                env_id=buffer_desc.env_id,
                main_id=buffer_desc.agent_id,
                pid=None,
                # pid=buffer_desc.policy_id,
            )
            table = self._tables[table_name]
            res = table.sample(size=self._sample_rate * buffer_desc.batch_size)
        except KeyError as e:
            info = f"data table `{table_name}` has not been created {list(self._tables.keys())}"
            res = None
        except OversampleError as e:
            info = f"No enough data: table_size={table.size} batch_size={buffer_desc.batch_size} table_name={table_name}"
            res = None
        except Exception as e:
            print(traceback.format_exc())
            res = None
            info = "others"
        return res, info

    def save(self, agent_episodes: Dict[AgentID, Episode], wait_for_ready: bool = True):
        raise NotImplementedError


@ray.remote
class OfflineDataset:
    def __init__(
        self, dataset_config: Dict[str, Any], exp_cfg: Dict[str, Any], test_mode=False
    ):
        self._episode_capacity = dataset_config.get(
            "episode_capacity", settings.DEFAULT_EPISODE_CAPACITY
        )
        self._learning_start = dataset_config.get("learning_start", 64)
        self._tables: Dict[str, Table] = dict()
        self._threading_lock = threading.Lock()
        self._threading_pool = ThreadPoolExecutor()
        if not test_mode:
            self.logger = get_logger(
                log_level=settings.LOG_LEVEL,
                log_dir=settings.LOG_DIR,
                name="offline_dataset",
                remote=settings.USE_REMOTE_LOGGER,
                mongo=settings.USE_MONGO_LOGGER,
                **exp_cfg,
            )
        else:
            self.logger = logging.getLogger("OfflineDataset")

        # parse init tasks
        init_job_config = dataset_config.get("init_job", {})
        if init_job_config.get("load_when_start"):
            path = init_job_config.get("path")
            if path:
                self.load(path)

        # Read-only proxies for external offline dataset
        external_resource_config = dataset_config.get("extern")
        self.external_proxy: List[ExternalDataset] = []
        if external_resource_config:
            for external_config, sample_rate in zip(
                external_resource_config["links"],
                external_resource_config["sample_rates"],
            ):
                if not external_config["write"]:
                    dataset = ExternalReadOnlyDataset(
                        name=external_config["name"],
                        path=external_config["path"],
                        sample_rate=sample_rate,
                    )
                    self.external_proxy.append(dataset)
                else:
                    raise NotImplementedError(
                        "External writable dataset is not supported"
                    )

        # quitting job
        quit_job_config = dataset_config.get("quit_job", {})
        self.dump_when_closed = quit_job_config.get("dump_when_closed")
        self.dump_path = quit_job_config.get("path")

    def lock(self, lock_type: str, desc: Dict[AgentID, BufferDescription]) -> str:
        """Lock table ready to push or pull and return the table status."""

        env_id = list(desc.values())[0].env_id
        main_ids = sorted(list(desc.keys()))
        table_name = Table.gen_table_name(
            env_id=env_id,
            main_id=main_ids,
            pid=[desc[aid].policy_id for aid in main_ids],
        )
        # check it is multi-agent or not
        self.check_table(table_name, None, is_multi_agent=len(main_ids) > 1)
        table = self._tables[table_name]
        status = table.lock_push_pull(lock_type)
        return status

    def unlock(self, lock_type: str, desc: Dict[AgentID, BufferDescription]):
        env_id = list(desc.values())[0].env_id
        main_ids = sorted(list(desc.keys()))
        table_name = Table.gen_table_name(
            env_id=env_id,
            main_id=main_ids,
            pid=[desc[aid].policy_id for aid in main_ids],
        )
        self.check_table(table_name, None, is_multi_agent=len(main_ids) > 1)
        table = self._tables[table_name]
        status = table.unlock_push_pull(lock_type)
        return status

    def create_table(self, buffer_desc: BufferDescription):
        name = Table.gen_table_name(
            env_id=buffer_desc.env_id,
            main_id=buffer_desc.agent_id,
            pid=buffer_desc.policy_id,
        )

        if name in self._tables:
            raise RepeatedAssignError("Table: {} exsited".format(name))
        self._tables[name] = Table(
            buffer_desc.agent_id,
            buffer_desc.capacity,
            buffer_desc.data_shapes,
            buffer_desc.sample_start_size,
        )

    def get_index(self, buffer_desc: BufferDescription) -> Union[List[int], None]:
        """Before saving, get index"""

        table_name = Table.gen_table_name(
            env_id=buffer_desc.env_id,
            main_id=buffer_desc.agent_id,
            pid=buffer_desc.policy_id,
        )
        table = self._tables[table_name]
        indexes = table.get_index(buffer_desc.batch_size)
        return indexes

    def save(self, buffer_desc: BufferDescription):
        table_name = Table.gen_table_name(
            env_id=buffer_desc.env_id,
            main_id=buffer_desc.agent_id,
            pid=buffer_desc.policy_id,
        )
        self.check_table(
            table_name, buffer_desc.data, is_multi_agent=len(buffer_desc.data) > 1
        )
        table = self._tables[table_name]
        table.insert(buffer_desc.indexes, buffer_desc.data)
        table.free_index(buffer_desc.indexes)

    @Log.method_timer(enable=settings.PROFILING)
    def load_from_dataset(
        self,
        file: str,
        env_id: str,
        policy_id: PolicyID,
        agent_id: AgentID,
    ):
        """
        Expect the dataset to be in the form of List[ Dict[str, Any] ]
        """

        # FIXME(ming): check its functionality
        with open(file, "rb") as f:
            dataset = pkl.load(file=f)
            keys = set()
            for batch in dataset:
                keys = keys.union(batch.keys())

            table_size = len(dataset)
            table_name = DATASET_TABLE_NAME_GEN(
                env_id=env_id,
                main_id=agent_id,
                pid=policy_id,
            )
            if self._tables.get(table_name, None) is None:
                self._tables[table_name] = Episode(
                    env_id, policy_id, other_columns=None
                )

            for batch in dataset:
                assert isinstance(batch, Dict)
                self._tables[table_name].insert(**batch)

    # @Log.method_timer(enable=settings.PROFILING)
    def load(self, path, mode="replace") -> List[Dict[str, str]]:
        table_descs = []
        with self._threading_lock:
            for fn in os.listdir(path):
                if fn.endswith(".tpkl"):
                    conflict_callback_required = False
                    table = Table.load(os.path.join(path, fn))
                    victim_table = None

                    if table.name in self._tables.keys() and mode.lower().equal(
                        "replace"
                    ):
                        victim_table = self.tables[table.name]
                        self.logger.debug(
                            f"Conflicts in loading table {table.name}, act as replacing"
                        )
                        try_lock_status = victim_table.lock_push_pull("push")
                        if try_lock_status != Status.NORMAL:
                            self.logger.error(
                                f"Try to replace an occupied table {victim_table.name}"
                            )
                        conflict_callback_required = True

                    self._tables[table.name] = table
                    table_descs.append(
                        {
                            "name": table.name,
                            "size": table.size,
                            "capacity": table.capacity,
                        }
                    )

                    if conflict_callback_required:
                        victim_table.unlock_push_pull("push")

            return table_descs

    # @Log.method_timer(enable=settings.PROFILING)
    def dump(self, path, table_names=None, as_csv=False):
        with self._threading_lock:
            if table_names is None:
                table_names = list(self._tables.keys())
            elif isinstance(table_names, str):
                table_names = [table_names]

            # Locking required tables
            status = dict.fromkeys(table_names, Status.FAILED)
            for tn in table_names:
                table = self._tables[tn]
                status[tn] = table.lock_push_pull("push")

            # Check locking status
            f = open("ds.log", "w")
            for tn, lock_status in status.items():
                f.write(f"Table {tn} lock status {lock_status}")
                if lock_status == Status.FAILED:
                    self.logger.info(
                        f"Failed to lock the table {tn}, skip the dumping."
                    )
                    continue
                if not as_csv:
                    self._tables[tn].dump(os.path.join(path, tn))
                else:
                    self._tables[tn].to_csv(os.path.join(path, tn))
                self._tables[tn].unlock_push_pull("push")
            f.close()
            return status

    # @Log.method_timer(enable=settings.PROFILING)
    def sample(self, buffer_desc: BufferDescription) -> Tuple[Batch, str]:
        """Sample data from the top for training, default is random sample from sub batches.

        :param BufferDesc buffer_desc: Description of sampling a buffer.
            used to index the buffer slot
        :return: a tuple of samples and information
        """

        # generate idxes from idxes manager
        res = {}
        info = "OK"
        # with Log.timer(log=settings.PROFILING, logger=self.logger):
        table_name = Table.gen_table_name(
            env_id=buffer_desc.env_id,
            main_id=buffer_desc.agent_id,
            pid=buffer_desc.policy_id,
        )
        table = self._tables[table_name]
        res = table.sample(buffer_desc.indexes)
        res = Batch(identity=buffer_desc.agent_id, data=res)
        return res, info

    def shutdown(self):
        status = None
        if self.dump_when_closed:
            self.logger.info("Begin OfflineDataset dumping.")
            status = self.dump(self.dump_path)
        self.logger.info("Server terminated.")
        return status
