#! /usr/bin/env python
# Copyright (c) 2019 Uber Technologies, Inc.
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
import argparse
import copy
import logging
import sys
from dataclasses import asdict
from typing import Any, Dict, List, Union

import yaml

from ludwig.constants import (
    BINARY,
    CATEGORY,
    COLUMN,
    COMBINER,
    DECODER,
    DEFAULTS,
    DROP_ROW,
    ENCODER,
    EXECUTOR,
    HYPEROPT,
    INPUT_FEATURES,
    LOSS,
    MODEL_ECD,
    MODEL_GBM,
    MODEL_TYPE,
    NAME,
    OUTPUT_FEATURES,
    PREPROCESSING,
    PROC_COLUMN,
    RAY,
    TRAINER,
    TYPE,
)
from ludwig.contrib import add_contrib_callback_args
from ludwig.data.split import get_splitter
from ludwig.features.feature_registries import base_type_registry, input_type_registry, output_type_registry
from ludwig.features.feature_utils import compute_feature_hash
from ludwig.globals import LUDWIG_VERSION
from ludwig.schema.combiners.utils import combiner_registry
from ludwig.schema.utils import load_config_with_kwargs, load_trainer_with_kwargs
from ludwig.utils.backward_compatibility import upgrade_deprecated_fields
from ludwig.utils.data_utils import load_config_from_str, load_yaml
from ludwig.utils.misc_utils import get_from_registry, merge_dict, set_default_value
from ludwig.utils.print_utils import print_ludwig

logger = logging.getLogger(__name__)

default_random_seed = 42

base_preprocessing_undersample_majority = None
base_preprocessing_oversample_minority = None
base_preprocessing_sample_ratio = 1.0

base_preprocessing_parameters = {
    "split": {},
    "undersample_majority": base_preprocessing_undersample_majority,
    "oversample_minority": base_preprocessing_oversample_minority,
    "sample_ratio": base_preprocessing_sample_ratio,
}

default_preprocessing_parameters = dict()

default_model_type = MODEL_ECD

default_combiner_type = "concat"


def _perform_sanity_checks(config):
    assert INPUT_FEATURES in config, "config does not define any input features"

    assert OUTPUT_FEATURES in config, "config does not define any output features"

    assert isinstance(config[INPUT_FEATURES], list), (
        "Ludwig expects input features in a list. Check your model " "config format"
    )

    assert isinstance(config[OUTPUT_FEATURES], list), (
        "Ludwig expects output features in a list. Check your model " "config format"
    )

    assert len(config[INPUT_FEATURES]) > 0, "config needs to have at least one input feature"

    assert len(config[OUTPUT_FEATURES]) > 0, "config needs to have at least one output feature"

    if TRAINER in config:
        assert isinstance(config[TRAINER], dict), (
            "There is an issue while reading the training section of the "
            "config. The parameters are expected to be"
            "read as a dictionary. Please check your config format."
        )

    if PREPROCESSING in config:
        assert isinstance(config[PREPROCESSING], dict), (
            "There is an issue while reading the preprocessing section of the "
            "config. The parameters are expected to be read"
            "as a dictionary. Please check your config format."
        )

    if COMBINER in config:
        assert isinstance(config[COMBINER], dict), (
            "There is an issue while reading the combiner section of the "
            "config. The parameters are expected to be read"
            "as a dictionary. Please check your config format."
        )

    if MODEL_TYPE in config:
        assert isinstance(
            config[MODEL_TYPE], str
        ), "Ludwig expects model type as a string. Please check your model config format."

    if DEFAULTS in config:
        defaults = config.get(DEFAULTS)

        for feature_type in list(defaults.keys()):
            # output_feature_types is a subset of input_feature_types so just check input_feature_types
            assert feature_type in set(
                input_type_registry.keys()
            ), f"""Defaults specified for `{feature_type}` but `{feature_type}` is
                not a feature type recognised by Ludwig."""

            feature_type_params = list(defaults.get(feature_type).keys())

            for feature_type_param in feature_type_params:
                assert feature_type_param in {
                    PREPROCESSING,
                    ENCODER,
                    DECODER,
                    LOSS,
                }, f"""`{feature_type_param}` is not a valid default parameter. Valid default parameters are
                    {PREPROCESSING}, {ENCODER}, {DECODER} and {LOSS}."""


def _set_feature_column(config: dict) -> None:
    for feature in config["input_features"] + config["output_features"]:
        if COLUMN not in feature:
            feature[COLUMN] = feature[NAME]


def _set_proc_column(config: dict) -> None:
    for feature in config["input_features"] + config["output_features"]:
        if PROC_COLUMN not in feature:
            feature[PROC_COLUMN] = compute_feature_hash(feature)


def _merge_hyperopt_with_trainer(config: dict) -> None:
    if "hyperopt" not in config:
        return

    scheduler = config["hyperopt"].get("executor", {}).get("scheduler")
    if not scheduler:
        return

    if TRAINER not in config:
        config[TRAINER] = {}

    # Disable early stopping when using a scheduler. We achieve this by setting the parameter
    # to -1, which ensures the condition to apply early stopping is never met.
    trainer = config[TRAINER]
    early_stop = trainer.get("early_stop")
    if early_stop is not None and early_stop != -1:
        raise ValueError(
            "Cannot set trainer parameter `early_stop` when using a hyperopt scheduler. "
            "Unset this parameter in your config."
        )
    trainer["early_stop"] = -1

    max_t = scheduler.get("max_t")
    time_attr = scheduler.get("time_attr")
    epochs = trainer.get("epochs")
    if max_t is not None:
        if time_attr == "time_total_s":
            if epochs is None:
                trainer["epochs"] = sys.maxsize  # continue training until time limit hit
            # else continue training until either time or trainer epochs limit hit
        elif epochs is not None and epochs != max_t:
            raise ValueError(
                "Cannot set trainer `epochs` when using hyperopt scheduler w/different training_iteration `max_t`. "
                "Unset one of these parameters in your config or make sure their values match."
            )
        else:
            trainer["epochs"] = max_t  # run trainer until scheduler epochs limit hit
    elif epochs is not None:
        scheduler["max_t"] = epochs  # run scheduler until trainer epochs limit hit


def _get_defaults_section_for_feature_type(
    feature_type: str,
    config_defaults: Dict[str, Dict[str, Any]],
    config_defaults_feature_types: List,
    config_defaults_section: str,
) -> Union[Dict[str, Any], Dict]:
    """Returns a dictionary of all default parameter values specified in the global defaults section for the
    config_defaults_section of the feature_type."""
    if feature_type in config_defaults_feature_types:
        if config_defaults_section in config_defaults.get(feature_type):
            return config_defaults.get(feature_type).get(config_defaults_section)
    return {}


def _merge_preprocessing_with_defaults(config_defaults: Dict[str, Any], config_default_feature_types: List[str]):
    """Update default_preprocessing_parameters that gets used by the preprocessing module."""
    global default_preprocessing_parameters
    for feature_type in config_default_feature_types:
        default_preprocessing_parameters[feature_type] = config_defaults.get(feature_type).get(PREPROCESSING, {})
    default_preprocessing_parameters = merge_dict(default_preprocessing_parameters, base_preprocessing_parameters)


def merge_with_defaults(config: dict) -> dict:  # noqa: F821
    config = copy.deepcopy(config)
    upgrade_deprecated_fields(config)
    _perform_sanity_checks(config)
    _set_feature_column(config)
    _set_proc_column(config)
    _merge_hyperopt_with_trainer(config)

    # ===== Defaults =====
    default_feature_specific_preprocessing_parameters = {
        name: base_type.preprocessing_defaults() for name, base_type in base_type_registry.items()
    }

    if DEFAULTS not in config:
        config[DEFAULTS] = dict()

    for feature_type, preprocessing_defaults in default_feature_specific_preprocessing_parameters.items():
        if feature_type not in config.get(DEFAULTS):
            config[DEFAULTS][feature_type] = {PREPROCESSING: preprocessing_defaults}
        elif PREPROCESSING not in config[DEFAULTS][feature_type]:
            config[DEFAULTS][feature_type][PREPROCESSING] = preprocessing_defaults
        else:
            config[DEFAULTS][feature_type][PREPROCESSING].update(
                merge_dict(preprocessing_defaults, config[DEFAULTS][feature_type][PREPROCESSING])
            )

    config_defaults = config.get(DEFAULTS)
    config_defaults_feature_types = list(config_defaults.keys())

    # ===== Preprocessing =====
    config[PREPROCESSING] = merge_dict(base_preprocessing_parameters, config.get(PREPROCESSING, {}))
    splitter = get_splitter(**config["preprocessing"].get("split", {}))
    splitter.validate(config)

    # Create global preprocessing dictionary for preprocessing module
    _merge_preprocessing_with_defaults(config_defaults, config_defaults_feature_types)

    stratify = config[PREPROCESSING]["stratify"]
    if stratify is not None:
        features = config[INPUT_FEATURES] + config[OUTPUT_FEATURES]
        feature_names = {f[COLUMN] for f in features}
        if stratify not in feature_names:
            logger.warning("Stratify is not among the features. " "Cannot establish if it is a binary or category")
        elif [f for f in features if f[COLUMN] == stratify][0][TYPE] not in {BINARY, CATEGORY}:
            raise ValueError("Stratify feature must be binary or category")

    # ===== Model Type =====
    set_default_value(config, MODEL_TYPE, default_model_type)

    # ===== Training =====
    # Convert config dictionary into an instance of BaseTrainerConfig.
    full_trainer_config, _ = load_trainer_with_kwargs(config[MODEL_TYPE], config[TRAINER] if TRAINER in config else {})
    config[TRAINER] = asdict(full_trainer_config)

    set_default_value(
        config[TRAINER],
        "validation_metric",
        output_type_registry[config[OUTPUT_FEATURES][0][TYPE]].default_validation_metric,
    )

    # ===== Input Features =====
    for input_feature in config[INPUT_FEATURES]:
        if config[MODEL_TYPE] == MODEL_GBM:
            input_feature[ENCODER] = "passthrough"
            remove_ecd_params(input_feature)
        get_from_registry(input_feature[TYPE], input_type_registry).populate_defaults(input_feature)

        # Update encoder parameters for input feature from global defaults
        default_encoder_params_for_feature_type = _get_defaults_section_for_feature_type(
            input_feature[TYPE],
            config_defaults,
            config_defaults_feature_types,
            ENCODER,
        )
        # TODO(#2125): Remove conditional check and copy creation once a PR for this issue is merged in
        if TYPE in default_encoder_params_for_feature_type:
            input_feature[ENCODER] = default_encoder_params_for_feature_type[TYPE]
        default_encoder_params_without_encoder_type = copy.deepcopy(default_encoder_params_for_feature_type)
        default_encoder_params_without_encoder_type.pop(TYPE, None)
        input_feature.update(merge_dict(input_feature, default_encoder_params_without_encoder_type))

    # ===== Combiner =====
    set_default_value(config, COMBINER, {TYPE: default_combiner_type})
    full_combiner_config, _ = load_config_with_kwargs(
        combiner_registry[config[COMBINER][TYPE]].get_schema_cls(), config[COMBINER]
    )
    config[COMBINER].update(asdict(full_combiner_config))

    # ===== Output features =====
    for output_feature in config[OUTPUT_FEATURES]:
        if config[MODEL_TYPE] == MODEL_GBM:
            output_feature[DECODER] = "passthrough"
            remove_ecd_params(output_feature)
        get_from_registry(output_feature[TYPE], output_type_registry).populate_defaults(output_feature)

        # By default, drop rows with missing output features
        set_default_value(output_feature, PREPROCESSING, {})
        set_default_value(output_feature[PREPROCESSING], "missing_value_strategy", DROP_ROW)

        # Update decoder parameters for output feature from global defaults
        default_decoder_params_for_feature_type = _get_defaults_section_for_feature_type(
            output_feature[TYPE],
            config_defaults,
            config_defaults_feature_types,
            DECODER,
        )
        # TODO(#2125): Remove conditional check and copy creation once a PR for this issue is merged in
        if TYPE in default_decoder_params_for_feature_type:
            output_feature[DECODER] = default_decoder_params_for_feature_type[TYPE]
        default_decoder_params_without_decoder_type = copy.deepcopy(default_decoder_params_for_feature_type)
        default_decoder_params_without_decoder_type.pop(TYPE, None)
        output_feature.update(merge_dict(output_feature, default_decoder_params_without_decoder_type))

        # Update loss parameters for output feature from global defaults
        default_loss_params_for_feature_type = _get_defaults_section_for_feature_type(
            output_feature[TYPE],
            config_defaults,
            config_defaults_feature_types,
            LOSS,
        )
        output_feature[LOSS].update(merge_dict(output_feature[LOSS], default_loss_params_for_feature_type))

    # ===== Hyperpot =====
    if HYPEROPT in config:
        set_default_value(config[HYPEROPT][EXECUTOR], TYPE, RAY)

    return config


def remove_ecd_params(feature):
    feature.pop("tied", None)
    feature.pop("fc_layers", None)
    feature.pop("num_layers", None)
    feature.pop("output_size", None)
    feature.pop("use_bias", None)
    feature.pop("weights_initializer", None)
    feature.pop("bias_initializer", None)
    feature.pop("norm", None)
    feature.pop("norm_params", None)
    feature.pop("activation", None)
    feature.pop("dropout", None)
    feature.pop("embedding_size", None)
    feature.pop("embeddings_on_cpu", None)
    feature.pop("pretrained_embeddings", None)
    feature.pop("embeddings_trainable", None)
    feature.pop("embedding_initializer", None)
    # decoder params
    feature.pop("reduce_input", None)
    feature.pop("dependencies", None)
    feature.pop("reduce_dependencies", None)
    feature.pop("loss", None)
    feature.pop("num_fc_layers", None)
    feature.pop("threshold", None)
    feature.pop("clip", None)
    feature.pop("top_k", None)


def render_config(config=None, output=None, **kwargs):
    output_config = merge_with_defaults(config)
    if output is None:
        print(yaml.safe_dump(output_config, None, sort_keys=False))
    else:
        with open(output, "w") as f:
            yaml.safe_dump(output_config, f, sort_keys=False)


def cli_render_config(sys_argv):
    parser = argparse.ArgumentParser(
        description="This script renders the full config from a user config.",
        prog="ludwig render_config",
        usage="%(prog)s [options]",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=load_yaml,
        help="Path to the YAML file containing the model configuration",
    )
    parser.add_argument(
        "-cs",
        "--config_str",
        dest="config",
        type=load_config_from_str,
        help="JSON or YAML serialized string of the model configuration",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="output rendered YAML config path",
        required=False,
    )

    add_contrib_callback_args(parser)
    args = parser.parse_args(sys_argv)

    args.callbacks = args.callbacks or []
    for callback in args.callbacks:
        callback.on_cmdline("render_config", *sys_argv)

    print_ludwig("Render Config", LUDWIG_VERSION)
    render_config(**vars(args))
