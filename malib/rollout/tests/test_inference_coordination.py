import time

from collections import defaultdict

import pytest
import ray

from malib import settings
from malib.common.strategy_spec import StrategySpec
from malib.envs import dummy_env
from malib.rollout.inference_client import InferenceClient
from malib.rollout.inference_server import InferenceWorkerSet

from tests.dataset import FakeDataServer
from tests.parameter_server import FakeParameterServer


@pytest.mark.parametrize("max_env_num", [1])
def test_inference_coordination(max_env_num: int):
    env_desc = dummy_env.env_desc_gen()
    agent_map_func = lambda agent: agent
    tmp_env = env_desc["creator"](**env_desc["config"])
    env_agents = tmp_env.possible_agents

    runtime_ids = set([agent_map_func(aid) for aid in tmp_env.possible_agents])

    if not ray.is_initialized():
        ray.init()

    offline_dataset_server = FakeDataServer.options(
        name=settings.OFFLINE_DATASET_ACTOR
    ).remote()
    parameter_server = FakeParameterServer.options(
        name=settings.PARAMETER_SERVER_ACTOR
    ).remote()

    client = InferenceClient(
        env_desc=env_desc,
        dataset_server=offline_dataset_server,
        max_env_num=max_env_num,
        use_subproc_env=False,
        batch_mode="time_step",
        postprocessor_types=["defaults"],
        training_agent_mapping=agent_map_func,
    )

    obs_spaces = env_desc["observation_spaces"]
    act_spaces = env_desc["action_spaces"]

    runtime_obs_spaces = {}
    runtime_act_spaces = {}

    # map agents
    agent_group = defaultdict(lambda: [])
    runtime_agent_ids = []
    for agent in env_agents:
        runtime_id = agent_map_func(agent)
        agent_group[runtime_id].append(agent)
        runtime_agent_ids.append(runtime_id)
    runtime_agent_ids = set(runtime_agent_ids)
    agent_group = dict(agent_group)

    for rid, agents in agent_group.items():
        runtime_obs_spaces[rid] = obs_spaces[agents[0]]
        runtime_act_spaces[rid] = act_spaces[agents[0]]

    servers = {
        runtime_id: InferenceWorkerSet.remote(
            agent_id=runtime_id,
            observation_space=runtime_obs_spaces[runtime_id],
            action_space=runtime_act_spaces[runtime_id],
            parameter_server=parameter_server,
            governed_agents=agent_group[runtime_id],
        )
        for runtime_id in runtime_ids
    }

    dataserver_entrypoint = f"test_inference_coordination_{time.time()}"

    policy_ids = ["dummy_0"]
    prob_list = [1.0]

    strategy_specs = {
        runtime_id: StrategySpec(
            policy_ids=policy_ids,
            meta_data={"prob_list": prob_list, "experiment_tag": experiment_tag},
        )
        for runtime_id in runtime_agent_ids
    }

    client.run(
        agent_interfaces=servers,
        desc=dict(
            flag="rollout",
            strategy_specs=strategy_specs,
            trainable_agents=env_agents,
            agent_group=agent_group,
            fragment_length=100,
            max_step=10,
        ),
        dataserver_entrypoint=dataserver_entrypoint,
    )
