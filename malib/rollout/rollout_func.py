"""
Users can register their rollout func here, with the same parameters list like method `sequential`
and return a Dict-like metric results.

Examples:
    >>> def custom_rollout_function(
    ...     agent_interfaces: List[env.AgentInterface],
    ...     env_desc: Dict[str, Any],
    ...     metric_type: str,
    ...     max_iter: int,
    ...     behavior_policy_mapping: Dict[AgentID, PolicyID],
    ... ) -> Dict[str, Any]

In your custom rollout function, you can decide extra data
you wanna save by specifying extra columns when Episode initialization.
"""

import collections
from dataclasses import dataclass
from numpy.core.numeric import roll
import ray
import numpy as np

from malib import settings
from malib.envs.env import Environment
from malib.utils.general import iter_many_dicts_recursively
from malib.utils.typing import (
    AgentID,
    AgentInvolveInfo,
    BufferDescription,
    Dict,
    Any,
    Tuple,
    List,
    BehaviorMode,
    DataTransferType,
    EnvID,
    Callable,
)
from malib.utils.logger import Log
from malib.utils.episode import Episode, NewEpisodeDict, EpisodeKey
from malib.rollout.postprocessor import get_postprocessor
from malib.envs.vector_env import VectorEnv, SubprocVecEnv
from malib.envs.agent_interface import AgentInterface


def _process_environment_returns(
    env_rets: Dict[EnvID, Dict[str, Dict[AgentID, Any]]],
    agent_interfaces: Dict[AgentID, AgentInterface],
    filtered_env_outputs: Dict[EnvID, Dict[str, Dict[AgentID, Any]]],
) -> Tuple[
    Dict[EnvID, Dict[str, Dict[AgentID, Any]]],
    Dict[EnvID, Dict[str, Dict[AgentID, Any]]],
    List[EnvID],
]:
    """Processes environment returns, including observation, rewards. Also the agent
    communication.
    """

    policy_inputs = {}
    drop_env_ids = []
    for env_id, rets in env_rets.items():
        policy_input = {}
        drop = False
        if env_id not in filtered_env_outputs:
            filtered_env_outputs[env_id] = {}
        filtered_env_output = filtered_env_outputs[env_id]
        for k, ret in rets.items():
            if k in [EpisodeKey.CUR_OBS, EpisodeKey.NEXT_OBS]:
                output = {
                    aid: interface.transform_observation(
                        observation=ret[aid], state=rets.get("state", None)
                    )["obs"]
                    for aid, interface in agent_interfaces.items()
                }
                if k == EpisodeKey.NEXT_OBS:
                    if EpisodeKey.CUR_OBS not in filtered_env_output:
                        filtered_env_output[EpisodeKey.CUR_OBS] = output
                    policy_input[EpisodeKey.CUR_OBS] = output
            else:
                # pop all done
                if k == EpisodeKey.DONE:
                    done = rets[EpisodeKey.DONE]["__all__"]
                    if done:
                        drop = True
                        drop_env_ids.append(env_id)
                    output = {k: v for k, v in ret.items() if k != "__all__"}
                else:
                    output = ret
            policy_input[k] = output
            filtered_env_output[k] = output

        # filtered_env_outputs[env_id] = output
        if not drop:
            policy_inputs[env_id] = policy_input

    return policy_inputs, filtered_env_outputs, drop_env_ids


def _do_policy_eval(
    policy_inputs: Dict[EnvID, Dict[str, Dict[AgentID, Any]]],
    agent_interfaces: Dict[AgentID, AgentInterface],
    episodes: NewEpisodeDict,
) -> Dict[str, Dict[EnvID, Dict[AgentID, Any]]]:
    actions, action_dists, next_rnn_state = {}, {}, {}

    env_ids = list(policy_inputs.keys())

    # collect by agent wise
    agent_wise_inputs = collections.defaultdict(
        lambda: collections.defaultdict(lambda: [])
    )
    for env_id in env_ids:
        env_episode = episodes[env_id]
        for agent_id, interface in agent_interfaces.items():
            # if interface.use_rnn:
            # then feed last rnn state here
            if len(env_episode[EpisodeKey.RNN_STATE][agent_id]) < 1:
                env_episode[EpisodeKey.RNN_STATE][agent_id].append(
                    interface.get_initial_state()
                )
            last_rnn_state = env_episode[EpisodeKey.RNN_STATE][agent_id][-1]
            agent_wise_inputs[agent_id][EpisodeKey.RNN_STATE].append(last_rnn_state)
        for k, agent_v in policy_inputs[env_id].items():
            for agent_id, v in agent_v.items():
                agent_wise_inputs[agent_id][k].append(v)

    for agent_id, interface in agent_interfaces.items():
        (
            actions[agent_id],
            action_dists[agent_id],
            next_rnn_state[agent_id],
        ) = interface.compute_action(**agent_wise_inputs[agent_id])

    return {
        EpisodeKey.ACTION: actions,
        EpisodeKey.ACTION_DIST: action_dists,
        EpisodeKey.RNN_STATE: next_rnn_state,
    }, env_ids


def _process_policy_outputs(
    env_ids: List[EnvID],
    policy_outputs: Dict[str, Dict[AgentID, DataTransferType]],
    env: Environment,
) -> Dict[EnvID, Dict[AgentID, Any]]:
    """Proceses the policy returns. Here we convert the policy return to legal environment step inputs."""

    assert (
        EpisodeKey.ACTION in policy_outputs and EpisodeKey.ACTION_DIST in policy_outputs
    ), "`action` and `action_prob` are required in the policy outputs, please check the return of `_do_policy_eval`: {}".format(
        list(policy_outputs.keys())
    )

    detached_policy_outputs = {}
    for i, env_id in enumerate(env_ids):
        detached = collections.defaultdict(lambda: collections.defaultdict())
        for k, agent_v in policy_outputs.items():
            for aid, _v in agent_v.items():
                detached[k][aid] = _v[i]
        detached_policy_outputs[env_id] = detached
    env_actions: Dict[EnvID, Dict[AgentID, Any]] = env.action_adapter(
        detached_policy_outputs
    )
    return env_actions, detached_policy_outputs


def _reduce_rollout_info(rollout_info) -> Dict[str, float]:
    res = {}
    if isinstance(rollout_info, list) or isinstance(rollout_info, tuple):
        _item = np.array(rollout_info)
        res["mean"] = np.mean(_item)
        res["min"] = np.min(_item)
        res["max"] = np.max(_item)
    elif isinstance(rollout_info, dict):
        for k, item in rollout_info.items():
            res[k] = _reduce_rollout_info(item)
    else:
        res = rollout_info

    return res


def env_runner(
    env: VectorEnv,
    agent_interfaces: Dict[AgentID, AgentInterface],
    buffer_desc: BufferDescription,
    runtime_config: Dict[str, Any],
    dataset_server: ray.ObjectRef = None,
    custom_environment_return_processor: Callable = None,
    custom_policy_output_processor: Callable = None,
    custom_do_policy_eval: Callable = None,
) -> Dict[str, Dict[str, Any]]:
    """Rollout in simultaneous mode, support environment vectorization.

    :param VectorEnv env: The environment instance.
    :param Dict[Agent,AgentInterface] agent_interfaces: The dict of agent interfaces for interacting with environment.
    :param ray.ObjectRef dataset_server: The offline dataset server handler, buffering data if it is not None.
    :return: A dict of rollout information.
    """

    # collect runtime configuration into runtime_config
    # keys in runtime config:
    #   1. num_envs: determines how many environments will this runner use
    #   2. max_step: the maximum length of one episode
    #   3. fragement_length: the total length you wanna run in this runner
    #   4. behavior_policies: a dict of policy ids, mapping from agent id to policy id
    behavior_policies = runtime_config["behavior_policies"]
    sample_dist = runtime_config.get("behavior_policy_dist", None)
    for agent_id, interface in agent_interfaces.items():
        interface.reset(policy_id=behavior_policies[agent_id], sample_dist=sample_dist)

    rets = env.reset(
        limits=runtime_config["num_envs"],
        fragment_length=runtime_config["fragment_length"],
        max_step=runtime_config["max_step"],
        custom_reset_config=runtime_config["custom_reset_config"],
    )
    if isinstance(env, VectorEnv):
        assert len(env.active_envs) > 0, (env._active_envs, rets, env)

    # if dataset_server:
    episodes = NewEpisodeDict(lambda env_id: Episode(behavior_policies, env_id=env_id))

    process_environment_returns = (
        custom_environment_return_processor or _process_environment_returns
    )
    process_policy_outputs = custom_policy_output_processor or _process_policy_outputs
    do_policy_eval = custom_do_policy_eval or _do_policy_eval

    while not env.is_terminated():
        filtered_env_outputs = {}
        # ============ a frame =============
        (
            active_policy_inputs,
            filtered_env_outputs,
            drop_env_ids,
        ) = process_environment_returns(rets, agent_interfaces, filtered_env_outputs)

        active_policy_outputs, active_env_ids = do_policy_eval(
            active_policy_inputs, agent_interfaces, episodes
        )

        env_inputs, detached_policy_outputs = process_policy_outputs(
            active_env_ids, active_policy_outputs, env
        )

        # XXX(ming): maybe more general inputs.
        rets = env.step(env_inputs)

        # again, filter next_obs here
        (
            active_policy_inputs,
            filtered_env_outputs,
            drop_env_ids,
        ) = process_environment_returns(rets, agent_interfaces, filtered_env_outputs)
        # filter policy inputs here
        # =================================
        a = set(list(detached_policy_outputs.keys()))
        b = set(list(filtered_env_outputs.keys()))
        assert len(b - a) >= 0

        episodes.record(detached_policy_outputs, filtered_env_outputs)

    rollout_info = env.collect_info()
    if dataset_server:
        policies = {
            aid: interface.get_policy(behavior_policies[aid])
            for aid, interface in agent_interfaces.items()
        }
        episodes: List[Dict[str, Dict[AgentID, np.ndarray]]] = get_postprocessor(
            runtime_config.get("post_processor_type", "default")
        )(list(episodes.to_numpy().values()), policies)

        buffer_desc.batch_size = env.batched_step_cnt
        indices = None
        while indices is None:
            batch = ray.get(dataset_server.get_producer_index.remote(buffer_desc))
            indices = batch.data
        # buffer_desc.batch_size = len(indices)
        buffer_desc.data = episodes
        buffer_desc.indices = indices
        dataset_server.save.remote(buffer_desc)

    ph = []
    for e in rollout_info.values():
        _e = _reduce_rollout_info(e)
        ph.append(e)

    holder = {}
    for history, ds, k, vs in iter_many_dicts_recursively(*ph, history=[]):
        _arr = np.array(vs)
        if len(_arr.shape) > 1:
            _arr = np.sum(_arr, axis=-1)
        prefix = "/".join(history)
        # print(history, prefix, _arr, vs)
        holder[prefix] = _arr

    return {"total_fragment_length": env.batched_step_cnt, "eval_info": holder}


class Stepping:
    def __init__(
        self,
        exp_cfg: Dict[str, Any],
        env_desc: Dict[str, Any],
        dataset_server=None,
        use_subproc_env: bool = False,
    ):

        # init environment here
        self.env_desc = env_desc

        # check whether env is simultaneous
        env = env_desc["creator"](**env_desc["config"])
        self._is_sequential = env.is_sequential

        if not env.is_sequential:
            if use_subproc_env:
                self.env = SubprocVecEnv(
                    env.observation_spaces,
                    env.action_spaces,
                    env_desc["creator"],
                    env_desc["config"],
                    max_num_envs=2,  # FIXME(ziyu): currently just fixed it.
                )
            else:
                self.env = VectorEnv(
                    observation_spaces=env.observation_spaces,
                    action_spaces=env.action_spaces,
                    creator=env_desc["creator"],
                    configs=env_desc["config"],
                )
            # self._default_callback = simultaneous
        else:
            self.env = env
            # self._default_callback = sequential

        self._dataset_server = dataset_server

    @classmethod
    def as_remote(
        cls,
        num_cpus: int = None,
        num_gpus: int = None,
        memory: int = None,
        object_store_memory: int = None,
        resources: dict = None,
    ) -> type:
        """Return a remote class for Actor initialization."""

        return ray.remote(
            num_cpus=num_cpus,
            num_gpus=num_gpus,
            memory=memory,
            object_store_memory=object_store_memory,
            resources=resources,
        )(cls)

    @Log.data_feedback(enable=settings.DATA_FEEDBACK)
    def run(
        self,
        agent_interfaces: Dict[AgentID, AgentInterface],
        fragment_length: int,
        desc: Dict[str, Any],
        callback: type,
        buffer_desc: BufferDescription = None,
    ) -> Tuple[str, Dict[str, List]]:
        """Environment stepping, rollout/simulate with environment vectorization if it is feasible.

        :param Dict[AgentID,AgentInterface] agent_interface: A dict of agent interfaces.
        :param Union[str,type] metric_type: Metric type or handler.
        :param int fragment_length: The maximum length of an episode.
        :param Dict[str,Any] desc: The description of task.
        :param type callback: Customized/registered rollout function.
        :param str role: Indicator of stepping type. Values in `rollout` or `simulation`.
        :returns: A tuple of a dict of MetricEntry and the caculation of total frames.
        """

        task_type = desc["flag"]
        behavior_policies = {}
        if task_type == "rollout":
            for interface in agent_interfaces.values():
                interface.set_behavior_mode(BehaviorMode.EXPLORATION)
        else:
            for interface in agent_interfaces.values():
                interface.set_behavior_mode(BehaviorMode.EXPLOITATION)

        # desc: policy_distribution, behavior_policies, num_episodes
        policy_distribution = desc.get("policy_distribution")
        for agent, interface in agent_interfaces.items():
            if policy_distribution:
                interface.reset(sample_dist=policy_distribution[agent])
            behavior_policies[agent] = interface.behavior_policy

        # behavior policies is a mapping from agents to policy ids
        # update with external behavior_policies
        behavior_policies.update(desc["behavior_policies"] or {})
        # specify the number of running episodes
        num_episodes = desc["num_episodes"]
        max_step = desc.get("max_step", -1)

        self.add_envs(num_episodes)

        rollout_results = env_runner(
            self.env,
            agent_interfaces,
            buffer_desc if task_type == "rollout" else None,
            runtime_config={
                "max_step": max_step,
                "fragment_length": fragment_length,
                "num_envs": num_episodes,
                "behavior_policies": behavior_policies,
                # FIXME(ming): custom reset config is closed here
                "custom_reset_config": None,
            },
            dataset_server=self._dataset_server if task_type == "rollout" else None,
        )
        return task_type, rollout_results

    def add_envs(self, maximum: int) -> int:
        """Create environments, if env is an instance of VectorEnv, add these new environment instances into it,
        otherwise do nothing.

        :returns: The number of nested environments.
        """

        if not isinstance(self.env, VectorEnv):
            return 1

        existing_env_num = getattr(self.env, "num_envs", 1)

        if existing_env_num >= maximum:
            return self.env.num_envs

        self.env.add_envs(num=maximum - existing_env_num)

        return self.env.num_envs

    def close(self):
        if self.env is not None:
            self.env.close()
