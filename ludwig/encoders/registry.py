from typing import Dict, List, Type, Union

from ludwig.api_annotations import DeveloperAPI
from ludwig.encoders.base import Encoder
from ludwig.utils.registry import Registry

encoder_registry = Registry()

sequence_encoder_registry = Registry()


@DeveloperAPI
def get_encoder_registry() -> Registry:
    return encoder_registry


@DeveloperAPI
def get_sequence_encoder_registry() -> Registry:
    return sequence_encoder_registry


def register_sequence_encoder(name: str):
    def wrap(cls):
        get_sequence_encoder_registry()[name] = cls
        return cls

    return wrap


def register_encoder(name: str, features: Union[str, List[str]]):
    if isinstance(features, str):
        features = [features]

    def wrap(cls):
        for feature in features:
            feature_registry = get_encoder_registry().get(feature, {})
            feature_registry[name] = cls
            get_encoder_registry()[feature] = feature_registry
        return cls

    return wrap


def get_encoder_cls(feature: str, name: str) -> Type[Encoder]:
    return get_encoder_registry()[feature][name]


def get_encoder_classes(feature: str) -> Dict[str, Type[Encoder]]:
    return get_encoder_registry()[feature]
