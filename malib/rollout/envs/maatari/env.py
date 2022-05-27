from typing import Dict, Any, Sequence, List

import importlib
import supersuit
import gym

from malib.rollout.envs import Environment
from malib.utils.typing import AgentID
from malib.utils.episode import Episode


def nested_env_creator(ori_creator: type, wrappers: Sequence[Dict]) -> type:
    """Wrap original atari environment creator with multiple wrappers"""

    def creator(**env_config):
        env = ori_creator(**env_config)
        # parse wrappers
        for wconfig in wrappers:
            name = wconfig["name"]
            params = wconfig["params"]

            wrapper = getattr(
                supersuit, name
            )  # importlib.import_module(f"supersuit.{env_desc['wrapper']['name']}")

            if isinstance(params, Sequence):
                env = wrapper(env, *params)
            elif isinstance(params, Dict):
                env = wrapper(env, **params)
            else:
                raise TypeError(f"Unexpected type: {type(params)}")
        return env

    return creator


class MAAtari(Environment):
    def __init__(self, **configs):
        super(MAAtari, self).__init__(**configs)

        env_id = self._configs["env_id"]
        scenario_configs = self._configs.get("scenario_configs", {})
        wrappers = self._configs.get("wrappers", {})
        env_module = env_module = importlib.import_module(f"pettingzoo.atari.{env_id}")
        ori_caller = env_module.parallel_env
        wrapped_caller = nested_env_creator(ori_caller, wrappers)

        self.is_sequential = False
        self.max_step = 1000

        self._env = wrapped_caller(**scenario_configs)
        self._trainable_agents = self._env.possible_agents
        self._observation_spaces = {
            aid: self._env.observation_space(aid) for aid in self.possible_agents
        }
        self._action_spaces = {
            aid: self._env.action_space(aid) for aid in self.possible_agents
        }

    @property
    def possible_agents(self) -> List[AgentID]:
        return self._env.possible_agents

    @property
    def observation_spaces(self) -> Dict[AgentID, gym.Space]:
        return self._observation_spaces

    @property
    def action_spaces(self) -> Dict[AgentID, gym.Space]:
        return self._action_spaces

    def time_step(self, actions: Dict[AgentID, Any]):
        observations, rewards, dones, infos = self._env.step(actions)
        return {
            Episode.NEXT_OBS: observations,
            Episode.REWARD: rewards,
            Episode.DONE: dones,
            Episode.INFO: infos,
        }

    def render(self, *args, **kwargs):
        pass

    def reset(self, *args, **kwargs):
        super(MAAtari, self).reset(*args, **kwargs)

        observations = self._env.reset()
        return {Episode.CUR_OBS: observations}

    def close(self):
        return self._env.close()
