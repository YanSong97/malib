import argparse

from pettingzoo.mpe import simple_v2

from malib.runner import run


parser = argparse.ArgumentParser("Async training on mpe environments.")

parser.add_argument("--num_learner", type=int, default=3)
parser.add_argument("--batch_size", type=int, default=64)
parser.add_argument("--num_epoch", type=int, default=100)
parser.add_argument("--algorithm", type=str, default="DQN")
parser.add_argument("--rollout_metric", type=str, default="simple", choices={"simple"})


if __name__ == "__main__":
    args = parser.parse_args()
    env_config = {
        "max_cycles": 25,
    }
    env = simple_v2.env(**env_config)
    possible_agents = env.possible_agents
    observation_spaces = env.observation_spaces
    action_spaces = env.action_spaces

    run(
        group="MPE/simple",
        name="async_dqn",
        worker_config={"worker_num": args.num_learner},
        env_description={
            "creator": simple_v2.env,
            "config": env_config,
            "id": "simple_v2",
            "possible_agents": possible_agents,
        },
        agent_mapping_func=lambda agent: [
            f"{agent}_async_{i}" for i in range(args.num_learner)
        ],
        training={
            "interface": {
                "type": "async",
                "observation_spaces": observation_spaces,
                "action_spaces": action_spaces,
                "population_size": -1,
            },
            "config": {
                "update_interval": 1,
                "saving_interval": 10,
                "batch_size": args.batch_size,
                "num_epoch": 100,
            },
        },
        algorithms={
            "Async": {"name": args.algorithm},
        },
        rollout={
            "type": "async",
            "stopper": "simple_rollout",
            "metric_type": args.rollout_metric,
            "fragment_length": env_config["max_cycles"],
            "num_episodes": 100,  # episode for each evaluation/training epoch
            "terminate": "any",
            "callback": "sequential",
        },
        global_evaluator={
            "name": "generic",
            "config": {"stop_metrics": {}},
        },
        dataset_config={"episode_capacity": 30000},
    )
