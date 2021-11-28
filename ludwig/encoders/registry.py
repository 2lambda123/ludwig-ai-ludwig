from typing import Union, List

from ludwig.utils.registry import Registry, DEFAULT_KEYS

encoder_registry = Registry()


def register_encoder(name: str, features: Union[str, List[str]], default=False):
    if isinstance(features, str):
        features = [features]

    def wrap(cls):
        for feature in features:
            feature_registry = encoder_registry.get(feature, {})
            feature_registry[name] = cls
            if default:
                for key in DEFAULT_KEYS:
                    feature_registry[key] = cls
            encoder_registry[feature] = feature_registry
        return cls

    return wrap


def get_encoder_cls(feature: str, name: str):
    return encoder_registry[feature][name]
