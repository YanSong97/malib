from typing import Any

import gym
import torch
import numpy as np

from torch.nn import functional as F

from malib.algorithm.common.policy import Policy
from malib.utils.typing import DataTransferType, Dict, Tuple, BehaviorMode, List
from malib.algorithm.common.model import get_model
from malib.utils.preprocessor import get_preprocessor
from malib.algorithm.common import misc
from malib.utils.episode import EpisodeKey


class DDPG(Policy):
    def __init__(
        self,
        registered_name: str,
        observation_space: gym.spaces.Space,
        action_space: gym.spaces.Space,
        model_config: Dict[str, Any] = None,
        custom_config: Dict[str, Any] = None,
        **kwargs
    ):
        super(DDPG, self).__init__(
            registered_name=registered_name,
            observation_space=observation_space,
            action_space=action_space,
            model_config=model_config,
            custom_config=custom_config,
        )

        action_dim = get_preprocessor(action_space)(action_space).size

        self._discrete_action = isinstance(action_space, gym.spaces.Discrete)
        if not self._discrete_action:
            self._exploration_callback = misc.OUNoise(action_dim)
        else:
            self._exploration_callback = misc.EPSGreedy(action_dim, threshold=0.3)

        self.set_actor(
            get_model(self.model_config.get("actor"))(
                observation_space, action_space, self.custom_config["use_cuda"]
            )
        )

        critic_state_space = gym.spaces.Dict(
            {"obs": observation_space, "act": action_space}
        )
        self.critic_preprocessor = get_preprocessor(critic_state_space)(
            critic_state_space
        )
        self.set_critic(
            get_model(self.model_config.get("critic"))(
                critic_state_space,
                gym.spaces.Discrete(1),
                self.custom_config["use_cuda"],
            )
        )
        self.target_actor = get_model(self.model_config.get("actor"))(
            observation_space, action_space, self.custom_config["use_cuda"]
        )
        self.target_critic = get_model(self.model_config.get("critic"))(
            critic_state_space, gym.spaces.Discrete(1), self.custom_config["use_cuda"]
        )

        self.register_state(self.actor, "actor")
        self.register_state(self.critic, "critic")
        self.register_state(self.target_actor, "target_actor")
        self.register_state(self.target_critic, "target_critic")

        self.update_target()

    def compute_actions(
        self, observation: DataTransferType, **kwargs
    ) -> DataTransferType:
        if self._discrete_action:
            pi = misc.gumbel_softmax(
                self.actor(observation), temperature=1.0, hard=True
            )
        else:
            pi = self.actor(observation)
        return pi

    def value_function(self, observation, **kwargs):
        with torch.no_grad():
            act_dist = np.asarray(kwargs["action_dist"])
            state = self.critic_preprocessor.transform(
                {"obs": observation, "act": kwargs["action_dist"]},
                nested=(len(act_dist.shape) > 1),
            )
            values = self.critic(state)
        return values.cpu().numpy().reshape(-1)

    def compute_action(
        self, observation: DataTransferType, **kwargs
    ) -> Tuple[DataTransferType, DataTransferType, List[DataTransferType]]:
        behavior = kwargs.get("behavior_mode", BehaviorMode.EXPLORATION)
        with torch.no_grad():
            # gumbel softmax convert to differentiable one-hot
            if self._discrete_action:
                if behavior == BehaviorMode.EXPLORATION:
                    pi = misc.gumbel_softmax(
                        self.actor(observation), temperature=1.0, hard=True
                    )
                else:
                    pi = misc.onehot_from_logits(self.actor(observation))
                act = pi.argmax(-1)
            else:
                pi = self.actor(observation)
                if behavior == BehaviorMode.EXPLORATION:
                    logits = self.actor(observation)
                    logits += torch.autograd.Variable(
                        torch.Tensor(np.random.standard_normal(logits.shape)),
                        requires_grad=False,
                    )
                act = pi
        rnn_state = kwargs[EpisodeKey.RNN_STATE]
        return act.numpy(), pi.numpy(), rnn_state

    def compute_actions_by_target_actor(
        self, observation: DataTransferType, **kwargs
    ) -> DataTransferType:
        with torch.no_grad():
            pi = self.target_actor(observation)
            if self._discrete_action:
                pi = misc.onehot_from_logits(pi)
        return pi

    def update_target(self):
        self.target_critic.load_state_dict(self._critic.state_dict())
        self.target_actor.load_state_dict(self._actor.state_dict())

    def soft_update(self, tau=0.01):
        misc.soft_update(self.target_critic, self.critic, tau)
        misc.soft_update(self.target_actor, self.actor, tau)
