import logging
from collections import deque
from pprint import pprint
from typing import Tuple

import pandas as pd
import pytest
import yaml

from ludwig.api import LudwigModel
from ludwig.config_validation.validation import get_schema
from ludwig.types import ModelConfigDict

from .configs import (
    COMBINER_TYPE_TO_COMBINE_FN_MAP,
    ECD_CONFIG_SECTION_TO_CONFIG,
    FEATURE_TYPE_TO_CONFIG_FOR_DECODER_LOSS,
    FEATURE_TYPE_TO_CONFIG_FOR_ENCODER_PREPROCESSING,
)
from .explore_schema import combine_configs, explore_properties


def defaults_config_generator(feature_type: str, only_include: str) -> Tuple[ModelConfigDict, pd.DataFrame]:
    """Generate combinatorial configs for the defaults section of the Ludwig config.

    Args:
        feature_type: feature type to explore.
        only_include: top-level parameter of the defaults sections that should be included.
    """
    assert isinstance(only_include, str)
    assert only_include in {"preprocessing", "encoder", "decoder", "loss"}

    schema = get_schema()
    properties = schema["properties"]["defaults"]["properties"][feature_type]["properties"]
    raw_entry = deque([(dict(), False)])
    explored = explore_properties(
        properties, parent_key="defaults." + feature_type, dq=raw_entry, only_include=[only_include]
    )

    if only_include in ["preprocessing", "encoder"]:
        config = FEATURE_TYPE_TO_CONFIG_FOR_ENCODER_PREPROCESSING[feature_type]
        config = yaml.safe_load(config)
    else:  # decoder and loss
        config = FEATURE_TYPE_TO_CONFIG_FOR_DECODER_LOSS[feature_type]
        config = yaml.safe_load(config)

    main_config_keys = list(config.keys())
    for key in main_config_keys:
        if key not in ["input_features", "output_features"]:
            del config[key]

    config["model_type"] = "ecd"
    config["trainer"] = {"train_steps": 1}
    for config, dataset in combine_configs(explored, config):
        yield config, dataset


def ecd_trainer_config_generator() -> Tuple[ModelConfigDict, pd.DataFrame]:
    """Generate combinatorial configs for the ECD trainer section of the Ludwig config."""
    schema = get_schema()
    properties = schema["properties"]

    raw_entry = deque([(dict(), False)])
    explored = explore_properties(properties, parent_key="", dq=raw_entry, only_include=["trainer"])
    config = ECD_CONFIG_SECTION_TO_CONFIG["trainer"]
    config = yaml.safe_load(config)
    config["model_type"] = "ecd"
    config["trainer"] = {"train_steps": 1}

    for config, dataset in combine_configs(explored, config):
        yield config, dataset


def combiner_config_generator(combiner_type: str) -> Tuple[ModelConfigDict, pd.DataFrame]:
    """Generate combinatorial configs for the combiner section of the Ludwig config.

    Args:
        combiner_type: combiner type to explore.
    """
    schema = get_schema()
    properties = schema["properties"]

    raw_entry = deque([(dict(), False)])
    explored = explore_properties(properties, parent_key="", dq=raw_entry, only_include=["combiner"])
    config = ECD_CONFIG_SECTION_TO_CONFIG[combiner_type]
    config = yaml.safe_load(config)
    config["model_type"] = "ecd"
    config["trainer"] = {"train_steps": 1}

    combine_configs_fn = COMBINER_TYPE_TO_COMBINE_FN_MAP[combiner_type]
    for config, dataset in combine_configs_fn(explored, config):
        if config["combiner"]["type"] == combiner_type:
            yield config, dataset


def train_and_evaluate(config: ModelConfigDict, dataset: pd.DataFrame):
    """Trains and evaluates a model with the given config.

    Args:
        config: valid Ludwig config.
        dataset: Ludwig dataset name to train on.
    """
    # adding print statements to be captured in pytest stdout and help debug tests.
    print("Config used (trained on synthetic data)")
    pprint(config)
    model = LudwigModel(config=config, callbacks=None, logging_level=logging.ERROR)
    model.train(dataset=dataset)
    model.evaluate(dataset=dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("sequence_concat"))
def test_ecd_sequence_concat_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("sequence"))
def test_ecd_sequence_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("comparator"))
def test_ecd_comparator_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("concat"))
def test_ecd_concat_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("project_aggregate"))
def test_ecd_project_aggregate_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("tabnet"))
def test_ecd_tabnet_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("tabtransformer"))
def test_ecd_tabtransformer_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", combiner_config_generator("transformer"))
def test_ecd_transformer_combiner(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", ecd_trainer_config_generator())
def test_ecd_trainer(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("number", "encoder"))
def test_number_encoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("number", "decoder"))
def test_number_decoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("number", "loss"))
def test_number_encoder_loss(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("number", "preprocessing"))
def test_number_preprocessing_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("category", "encoder"))
def test_category_encoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("category", "decoder"))
def test_category_decoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("category", "loss"))
def test_category_loss_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("category", "preprocessing"))
def test_category_preprocessing_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("binary", "encoder"))
def test_binary_encoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("binary", "decoder"))
def test_binary_decoder_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("binary", "loss"))
def test_binary_loss_defaults(config, dataset):
    train_and_evaluate(config, dataset)


@pytest.mark.combinatorial
@pytest.mark.parametrize("config,dataset", defaults_config_generator("binary", "preprocessing"))
def test_binary_preprocessing_defaults(config, dataset):
    train_and_evaluate(config, dataset)


# @pytest.mark.combinatorial
# @pytest.mark.parametrize("config,dataset", defaults_config_generator("text", "preprocessing"))
# def test_text_preprocessing_defaults(config, dataset):
#     train_and_evaluate(config, dataset)


# @pytest.mark.combinatorial
# @pytest.mark.parametrize("config,dataset", defaults_config_generator("text", "encoder"))
# def test_text_encoder_defaults(config):
#     train_and_evaluate(config, dataset)
