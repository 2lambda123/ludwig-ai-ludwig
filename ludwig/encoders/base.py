#! /usr/bin/env python
# Copyright (c) 2020 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from abc import ABC, abstractmethod
from typing import Any, Dict

from torch import nn

from ludwig.api_annotations import DeveloperAPI
from ludwig.utils.torch_utils import LudwigModule


@DeveloperAPI
class Encoder(LudwigModule, ABC):
    @abstractmethod
    def forward(self, inputs, training=None, mask=None):
        raise NotImplementedError

    def get_embedding_layer(self) -> nn.Module:
        """Returns layer that embeds inputs, used for computing explanations."""
        return next(self.children())

    @property
    def name(self):
        return self.__class__.__name__

    @classmethod
    def get_fixed_preprocessing_params(cls, encoder_params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns a dict of fixed preprocessing parameters for the encoder if required."""
        return {}

    @classmethod
    def is_pretrained(cls, encoder_params: Dict[str, Any]) -> bool:
        return False

    @classmethod
    def can_cache_embeddings(cls, encoder_params: Dict[str, Any]) -> bool:
        """Returns true if the encoder's output embeddings will not change during training."""
        return False
