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

import uuid
import ray
import collections
import numpy as np
import time

from pettingzoo.utils.env import AECEnv

from malib import settings
from malib.utils.logger import Log, Logger
from malib.utils.typing import (
    AgentID,
    BufferDescription,
    Dict,
    PolicyID,
    Union,
    Any,
    Tuple,
    List,
    BehaviorMode,
    Callable,
)
from malib.utils.preprocessor import get_preprocessor
from malib.envs.env import EpisodeInfo
from malib.envs import Environment
from malib.envs.agent_interface import AgentInterface
from malib.envs.vector_env import VectorEnv
from malib.backend.datapool.offline_dataset_server import Episode


def _parse_episode_infos(episode_infos: List[EpisodeInfo]) -> Dict[str, List]:
    res = {}
    for episode_info in episode_infos:
        for k, v in episode_info.step_cnt.items():
            k = f"step_cnt/{k}"
            if res.get(k) is None:
                res[k] = []
            res[k].append(v)
        for k, v in episode_info.total_rewards.items():
            k = f"total_reward/{k}"
            if res.get(k) is None:
                res[k] = []
            res[k].append(v)
        # extra_info = episode_info.extra_info
        # if len(extra_info) > 0:
        #     for k, v in extra_info.items():
        #         res["custom_metric"]
    return res


_TimeStep = collections.namedtuple(
    "_TimeStep", "observation, action_mask, reward, action, done, action_dist"
)


def sequential(
    env: AECEnv,
    num_episodes: int,
    agent_interfaces: Dict[AgentID, AgentInterface],
    fragment_length: int,
    max_step: int,
    behavior_policies: Dict[AgentID, PolicyID],
    buffer_description: BufferDescription,
    send_interval: int = 50,
    dataset_server: ray.ObjectRef = None,
):
    """ Rollout in sequential manner """

    cnt = 0

    if buffer_description is not None:
        agent_filters = buffer_description.agent_id
        buffer_indices = None
        while buffer_indices is not None:
            buffer_indices = ray.get(dataset_server.requeste_producer_index.remote(buffer_description))
            time.sleep(0.5)
        buffer_description.indices = buffer_indices
    else:
        agent_filters = list(agent_interfaces.keys())

    total_cnt = {agent: 0 for agent in agent_filters}
    mean_episode_reward = collections.defaultdict(list)
    mean_episode_len = collections.defaultdict(list)
    win_rate = collections.defaultdict(list)

    while any(
        [agent_total_cnt < fragment_length for agent_total_cnt in total_cnt.values()]
    ):
        env.reset()
        cnt = collections.defaultdict(lambda: 0)
        tmp_buffer = collections.defaultdict(list)
        episode_reward = collections.defaultdict(lambda: 0.0)

        for aid in env.agent_iter(max_iter=max_step):
            observation, reward, done, info = env.last()
            action_mask = np.asarray(observation["action_mask"])

            # observation has been transferred
            observation = agent_interfaces[aid].transform_observation(
                observation, behavior_policies[aid]
            )
            if not done:
                action, action_dist, _ = agent_interfaces[aid].compute_action(
                    observation,
                    action_mask=action_mask,
                    policy_id=behavior_policies[aid],
                )
                # convert action to scalar
            else:
                info["policy_id"] = behavior_policies[aid]
                action = None
            env.step(action)

            if dataset_server and aid in buffer_description.agent_id:
                tmp_buffer[aid].append(
                    _TimeStep(
                        observation,
                        action_mask,
                        reward,
                        action
                        if action is not None
                        else env.action_spaces[aid].sample(),
                        done,
                        action_dist,
                    )
                )
            episode_reward[aid] += reward
            cnt[aid] += 1

            if all([agent_cnt >= fragment_length for agent_cnt in cnt.values()]):
                break
        winner, max_reward = None, -float("inf")
        total_cnt = {aid: v + cnt[aid] for aid, v in total_cnt.items()}

        for k, v in episode_reward.items():
            mean_episode_reward[k].append(v)
            mean_episode_len[k].append(cnt[k])
            if v > max_reward:
                winner = k
                max_reward = v
        for k in agent_filters:
            if k == winner:
                win_rate[winner].append(1)
            else:
                win_rate[k].append(0)

    Logger.debug("agent total_cnt: %s fragment length: %s", total_cnt, fragment_length)
    if dataset_server:
        for player, data_tups in tmp_buffer.items():
            (
                observations,
                action_masks,
                pre_rewards,
                actions,
                dones,
                action_dists,
            ) = tuple(map(np.stack, list(zip(*data_tups))))

            rewards = pre_rewards[1:].copy()
            dones = dones[1:].copy()
            next_observations = observations[1:].copy()
            next_action_masks = action_masks[1:].copy()

            observations = observations[:-1].copy()
            action_masks = action_masks[:-1].copy()
            actions = actions[:-1].copy()
            action_dists = action_dists[:-1].copy()

            buffer_description.data[player].insert(
                **{
                    Episode.CUR_OBS: observations,
                    Episode.NEXT_OBS: next_observations,
                    Episode.REWARD: rewards,
                    Episode.ACTION: actions,
                    Episode.DONE: dones,
                    Episode.ACTION_DIST: action_dists,
                    Episode.ACTION_MASK: action_masks,
                    Episode.NEXT_ACTION_MASK: next_action_masks,
                }
            )
        dataset_server.save.remote(buffer_description)

    results = {
        f"total_reward/{k}": v
        for k, v in mean_episode_reward.items()
        if k in agent_filters
    }
    results.update(
        {f"step_cnt/{k}": v for k, v in mean_episode_len.items() if k in agent_filters}
    )
    results.update(
        {f"win_rate/{k}": v for k, v in win_rate.items() if k in agent_filters}
    )

    # aggregated evaluated results groupped in agent wise
    return results, sum(total_cnt.values())


def simultaneous(
    env: VectorEnv,
    num_envs: int,
    agent_interfaces: Dict[AgentID, AgentInterface],
    fragment_length: int,
    max_step: int,
    behavior_policies: Dict[AgentID, PolicyID],
    agent_episodes: Dict[AgentID, Episode],
    send_interval: int = 50,
    dataset_server: ray.ObjectRef = None,
):
    """Rollout in simultaneous mode, support environment vectorization.

    :param VectorEnv env: The environment instance.
    :param int num_envs: The number of parallel environments.
    :param Dict[Agent,AgentInterface] agent_interfaces: The dict of agent interfaces for interacting with environment.
    :param int fragment_length: The maximum step limitation of environment rollout.
    :param Dict[AgentID,PolicyID] behavior_policies: The behavior policy mapping for policy
        specifing when execute `compute_action` `transform_observation. Furthermore, the specified policy id will replace the existing behavior policy if you've reset it before.
    :param Dict[AgentID,Episode] agent_episodes: A dict of agent episodes, for individual experience buffering.
    :param Metric metric: The metric handler, for statistics parsing and grouping.
    :param int send_interval: Specifying the step interval of sending buffering data to remote offline dataset server.
    :param ray.ObjectRef dataset_server: The offline dataset server handler, buffering data if it is not None.
    :return: A tuple of statistics and the size of buffered experience.
    """

    rets = env.reset(
        limits=num_envs,
        fragment_length=fragment_length,
        env_reset_kwargs={"max_step": max_step},
    )

    observations = {
        aid: agent_interfaces[aid].transform_observation(obs)
        for aid, obs in rets[Episode.CUR_OBS].items()
    }

    while not env.is_terminated():
        actions, action_dists, action_masks = {}, {}, {}
        for aid, observation in observations.items():
            action_masks[aid] = (
                rets[Episode.ACTION_MASK][aid]
                if rets.get(Episode.ACTION_MASK) is not None
                else None
            )
            actions[aid], action_dists[aid], _ = agent_interfaces[aid].compute_action(
                observation,
                policy_id=behavior_policies[aid],
                action_mask=action_masks[aid],
            )
        rets = env.step(actions)

        next_observations = {
            aid: agent_interfaces[aid].transform_observation(obs)
            for aid, obs in rets[Episode.CUR_OBS].items()
        }

        if dataset_server:
            for aid in env.trainable_agents:
                agent_episodes[aid].insert(
                    **{
                        Episode.CUR_OBS: observations[aid],
                        Episode.NEXT_OBS: next_observations[aid],
                        Episode.REWARD: rets[Episode.REWARD][aid],
                        Episode.ACTION: actions[aid],
                        Episode.DONE: rets[Episode.DONE][aid],
                        Episode.ACTION_DIST: action_dists[aid],
                    }
                )
        observations = next_observations

    if dataset_server:
        # request indices
        agent_ids = list(agent_episodes.keys())
        policy_ids = [behavior_policies[aid] for aid in agent_ids]
        buffer_desc = BufferDescription(env.env_configs["env_id"], agent_ids, policy_ids, batch_size=sum(episode.size() for episode in agent_episodes.values()))
        while buffer_indices is None:
            buffer_indices = ray.get(dataset_server.request_producer_index.remote(buffer_desc))
            time.sleep(0.5)
        buffer_desc.indices = buffer_indices
        dataset_server.save.remote(buffer_desc)

    results = _parse_episode_infos(env.epsiode_infos)
    return results, env.batched_step_cnt * len(env.possible_agents)


def get_func(name: Union[str, Callable]):
    if callable(name):
        return name
    else:
        return {"sequential": sequential, "simultaneous": simultaneous}[name]


class Stepping:
    def __init__(
        self, exp_cfg: Dict[str, Any], env_desc: Dict[str, Any], dataset_server=None
    ):
        # init environment here
        self.env_desc = env_desc

        # check whether env is simultaneous
        env = env_desc["creator"](**env_desc["config"])
        self._is_sequential = env.is_sequential

        if not env.is_sequential:
            self.env = VectorEnv.from_envs([env], config=env_desc["config"])
            self.callback = simultaneous
        else:
            self.env = env
            self.callback = sequential

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
        episode_buffers: Dict[AgentID, Episode] = None,
    ) -> Tuple[str, Dict[str, List], int]:
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
                interface.reset(policy_distribution[agent])
            behavior_policies[agent] = interface.behavior_policy

        # behavior policies is a mapping from agents to policy ids
        # update with external behavior_policies
        behavior_policies.update(desc["behavior_policies"])
        # specify the number of running episodes
        num_episodes = desc["num_episodes"]
        max_step = desc.get("max_step", 1000)

        self.add_envs(num_episodes)

        if task_type == "rollout":
            episode_buffers = episode_buffers or {
                agent: Episode(
                    self.env_desc["config"]["env_id"],
                    desc["behavior_policies"][agent],
                    capacity=fragment_length,
                    other_columns=self.env.extra_returns,
                )
                for agent in desc["behavior_policies"]
            }
        else:
            episode_buffers = None

        callback = get_func(callback) if callback else self.callback

        evaluated_results, num_frames = callback(
            self.env,
            num_episodes,
            agent_interfaces,
            fragment_length,
            max_step,
            behavior_policies,
            episode_buffers,
            dataset_server=self._dataset_server if task_type == "rollout" else None,
        )
        return task_type, evaluated_results, num_frames

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
