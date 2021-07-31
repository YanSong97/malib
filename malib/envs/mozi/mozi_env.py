import numpy as np

from gym import spaces
from pettingzoo import ParallelEnv
from malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank.env_uav_anti_tank import EnvUavAntiTank
import malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank.etc_uav_anti_tank as etc_uav_anti_tank

from malib.envs import Environment
from malib.utils.typing import Dict, AgentID, Any
from malib.backend.datapool.offline_dataset_server import Episode

maps = {
    "uav_anti_tank": {
        "env": EnvUavAntiTank,
        "etc": etc_uav_anti_tank,
        "agents_list": [f"Aircrafts_{i}" for i in range(1)]
    }
}


class _MoZiEnv(ParallelEnv):

    def __init__(self, **kwargs):
        super(_MoZiEnv, self).__init__()
        map_config = maps[kwargs["map_name"]]
        etc = map_config["etc"]
        self.real_env = map_config["env"](etc.SERVER_IP,
                                          etc.SERVER_PORT,
                                          etc.SCENARIO_NAME,
                                          etc.SIMULATE_COMPRESSION,
                                          etc.DURATION_INTERVAL,
                                          etc.SERVER_PLAT)
        self.possible_agents = map_config["agents_list"]
        self.n_agents = len(self.possible_agents)
        self.agents = self.possible_agents

        n_obs = self.real_env.state_space_dim
        num_actions = self.real_env.action_space_dim
        action_limit = self.real_env.action_max
        self.observation_spaces = dict(
            zip(
                self.possible_agents,
                [
                    spaces.Dict(
                        {
                            "observation": spaces.Box(
                                low=0.0, high=1.0, shape=(n_obs,), dtype=np.float
                            )
                        }
                    )
                    for _ in range(self.n_agents)
                ],
            )
        )

        self.action_spaces = dict(
            zip(
                self.possible_agents,
                [spaces.Box(
                    low=-action_limit, high=action_limit, shape=(num_actions,), dtype=np.float
                ) for _ in range(self.n_agents)
                ],
            )
        )

    def reset(self):
        """only return observation not return state"""
        self.agents = self.possible_agents
        obs_0, _ = self.real_env.reset()
        obs = {
            # aid: {"observation": obs_0[i]}
            aid: {"observation": np.array(obs_0)}  # single-agent env has only one obs
            for i, aid in enumerate(self.agents)
        }
        return obs

    def step(self, actions):
        act_list = [actions[aid][0] for aid in self.agents]
        obs_t_next, reward_t = self.real_env.execute_action(act_list)
        done_t = self.real_env.check_done()

        rew_dict = {agent: reward_t for agent in self.agents}
        done_dict = {agent: done_t for agent in self.agents}
        next_obs_dict = {
            aid: {
                # "observation": next_obs_t[i]
                "observation": obs_t_next  # single-agent env has only one obs
            }
            for i, aid in enumerate(self.agents)
        }

        if done_t:
            self.agents = []
        return (
            next_obs_dict,
            rew_dict,
            done_dict
        )


class MoZiEnv(Environment):
    def __init__(self, **configs):
        super(MoZiEnv, self).__init__(**configs)

        self.is_sequential = False
        self._env_id = configs["env_id"]
        self._env = _MoZiEnv(**configs["scenario_configs"])
        self._trainable_agents = self._env.possible_agents

    def step(self, actions: Dict[AgentID, Any]):
        observations, rewards, dones = self._env.step(actions)
        return {
            Episode.NEXT_OBS: observations,
            Episode.REWARD: rewards,
            Episode.DONE: dones
        }

    def render(self, *args, **kwargs):
        self._env.render()

    def reset(self):
        observations = self._env.reset()
        return {Episode.CUR_OBS: observations}


if __name__ == "__main__":
    env_config = {"scenario_configs": {"map_name": "uav_anti_tank"}, "env_id": "test"}
    env = MoZiEnv(**env_config)
    print("POSSIBLE AGENTS:", env.possible_agents)
    print("OBSERVATION SPACES:", env.observation_spaces)
    print("ACTION_SPACES:", env.action_spaces)

    respone = env.reset()
    obs = respone[Episode.CUR_OBS]
    while True:
        act_dict = {}
        for i, aid in enumerate(env.possible_agents):
            act_dict[aid] = np.random.random(1) * 2 - 1  # [-1, 1)
        print(act_dict)
        print(obs)
        respone = env.step(act_dict)
        obs = respone[Episode.NEXT_OBS]
        rew = respone[Episode.REWARD]
        done = respone[Episode.DONE]
        print(rew, done)
        if all(done.values()):
            break
