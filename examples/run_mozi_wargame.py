import argparse
from malib.envs.mozi import MoZiEnv
import os
import yaml
from malib.runner import run


if __name__ == "__main__":

    env_config = {"scenario_configs": {"map_name": "uav_anti_tank"}, "env_id": "test"}

    env = MoZiEnv(**env_config)
    possible_agents = env.possible_agents
    observation_spaces = env.observation_spaces
    action_spaces = env.action_spaces
    print("ACTION SPACES:", action_spaces)
    print("OBSERVATION SPACES:", observation_spaces)
    env.close()
    run(
        group="MoZi",
        name="simple_try",
        env_description={
            "creator": MoZiEnv,
            "config": env_config,
            "possible_agents": possible_agents,
        },
        agent_mapping_func=lambda agent: agent,
        training={
            "interface": {
                "type": "independent",
                "observation_spaces": observation_spaces,
                "action_spaces": action_spaces,
            },
            "config": {
                "update_interval": 1,
                "saving_interval": 10,
                "batch_size": 128,
                "optimizer": "Adam",
                "actor_lr": 0.001,
                "critic_lr": 0.001,
                "lr": 0.001,
                "tau": 0.01,
                "grad_norm_clipping": 0.5,
            },
        },
        algorithms={
            "PPO": {
                "name": "PPO",
                "model_config": {
                    "critic": {
                        "network": "mlp",
                        "layers": [
                            {"units": 16, "activation": "ReLU"},
                            {"units": 16, "activation": "ReLU"},
                        ],
                        "output": {
                            "activation": False
                        }
                    },
                    "actor": {
                        "network": "mlp",
                        "layers": [
                            {"units": 16, "activation": "ReLU"},
                            {"units": 16, "activation": "ReLU"},
                        ],
                        "output": {
                            "activation": False
                        }
                    }
                },
                "custom_config": {
                    "lr": 1e-3,
                },
            }
        },
        rollout={
            "type": "async",
            "stopper": "simple_rollout",
            "stopper_config": {"max_step": 100},
            "metric_type": "simple",
            "fragment_length": 1000,
            "num_episodes": 1,  # parallel env num in each worker
            "episode_seg": 1,
            "terminate": "any",
        },
        evaluation={"fragment_length": 100, "num_episodes": 100},
        global_evaluator={"name": "generic"},
    )
