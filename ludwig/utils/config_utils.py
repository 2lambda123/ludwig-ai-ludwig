from typing import Any, Dict, Set, Union

from ludwig.constants import DECODER, DEFAULTS, ENCODER, INPUT_FEATURES, LOSS, PREPROCESSING, TYPE
from ludwig.features.feature_registries import input_type_registry, output_type_registry
from ludwig.schema.config_object import Config
from ludwig.utils.misc_utils import get_from_registry


def remove_excess_params(config):
    """This is a helper function for removing excess params that end up on the config after setting the defaults
    via the config object.

    Args:
        config: Config dictionary with excess params to remove

    Returns:
        None -> Modifies config dict
    """
    for feature_type in config[DEFAULTS].keys():
        excess_params = []
        for module in config[DEFAULTS][feature_type]:
            if module not in {PREPROCESSING, ENCODER, DECODER, LOSS}:
                excess_params.append(module)
        for param in excess_params:
            del config[DEFAULTS][feature_type][param]


def get_feature_type_parameter_values_from_section(
    config: Dict[str, Any], features_section: str, feature_type: str, parameter_name: str
) -> Set:
    """Returns the set of all parameter values used for the given features_section, feature_type, and
    parameter_name."""
    parameter_values = set()
    for feature in config[features_section]:
        if feature[TYPE] == feature_type:
            if parameter_name in feature:
                parameter_values.add(feature[parameter_name])
            elif parameter_name in feature[ENCODER]:
                parameter_values.add(feature[ENCODER][parameter_name])
            elif parameter_name in feature[DECODER]:
                parameter_values.add(feature[DECODER][parameter_name])
    return parameter_values


def get_defaults_section_for_feature_type(
    feature_type: str,
    config_defaults: Dict[str, Dict[str, Any]],
    config_defaults_section: str,
) -> Union[Dict[str, Any], Dict]:
    """Returns a dictionary of all default parameter values specified in the global defaults section for the
    config_defaults_section of the feature_type."""

    if feature_type not in config_defaults:
        return {}

    if config_defaults_section not in config_defaults[feature_type]:
        return {}

    return config_defaults[feature_type][config_defaults_section]


def get_preprocessing_params(config_obj: Config) -> Dict[str, Any]:
    """Returns a new dictionary that merges preprocessing section of config with type-specific preprocessing
    parameters from config defaults."""
    preprocessing_params = {}
    preprocessing_params.update(config_obj.preprocessing.to_dict())
    for feat_type in input_type_registry.keys():
        preprocessing_params[feat_type] = getattr(config_obj.defaults, feat_type).preprocessing.to_dict()
    return preprocessing_params


def get_default_encoder_or_decoder(feature: Dict[str, Any], config_feature_group: str) -> str:
    """Returns the default encoder or decoder for a feature."""
    if config_feature_group == INPUT_FEATURES:
        feature_schema = get_from_registry(feature.get(TYPE), input_type_registry).get_schema_cls()
        return feature_schema().encoder.type
    feature_schema = get_from_registry(feature.get(TYPE), output_type_registry).get_schema_cls()
    return feature_schema().decoder.type
