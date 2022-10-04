import os
from tempfile import TemporaryDirectory

import yaml

from ludwig.constants import COMBINER, DEFAULTS, HYPEROPT, INPUT_FEATURES, OUTPUT_FEATURES, PREPROCESSING, TRAINER
from ludwig.schema.config_object import Config


def test_config_object():
    config = {
        "input_features": [
            {
                "name": "text_feature",
                "type": "text",
                "preprocessing": {
                    "missing_value_strategy": "drop_row",
                },
                "encoder": {
                    "type": "rnn",
                    "bidirectional": True,
                    "representation": "dense",
                    "num_layers": 2,
                },
            },
            {
                "name": "image_feature_1",
                "type": "image",
                "preprocessing": {
                    "height": 7.5,
                    "width": 7.5,
                    "num_channels": 4,
                },
                "encoder": {
                    "type": "resnet",
                    "num_channels": 4,
                    "dropout": 0.1,
                    "resnet_size": 100,
                },
            },
        ],
        "output_features": [
            {
                "name": "category_feature",
                "type": "category",
                "top_k": 3,
                "preprocessing": {
                    "missing_value_strategy": "backfill",
                },
                "decoder": {
                    "type": "classifier",
                    "num_classes": 10,
                    "use_bias": False,
                },
            },
        ],
        "combiner": {
            "type": "concat",
            "output_size": 512,
            "weights_initializer": "xavier_uniform",
            "dropout": 0.2,
        },
        "trainer": {
            "epochs": 50,
            "batch_size": "auto",
            "optimizer": {
                "type": "adam",
                "beta1": 0.8,
                "beta2": 0.999,
                "epsilon": 5e-09,
            },
        },
    }

    config_object = Config.from_dict(config)
    assert config_object.input_features.text_feature.encoder.type == "rnn"
    assert config_object.input_features.text_feature.encoder.num_layers == 2

    assert config_object.output_features.category_feature.decoder.num_classes == 10
    assert config_object.output_features.category_feature.top_k == 3

    assert config_object.combiner.output_size == 512
    assert config_object.combiner.weights_initializer == "xavier_uniform"
    assert config_object.combiner.fc_layers is None

    assert config_object.trainer.epochs == 50
    assert config_object.trainer.batch_size == "auto"

    assert config_object.trainer.optimizer.type == "adam"
    assert config_object.trainer.optimizer.beta1 == 0.8
    assert config_object.trainer.optimizer.beta2 == 0.999
    assert config_object.trainer.optimizer.epsilon == 5e-09


def test_config_object_defaults():
    config = {
        "input_features": [
            {"name": "number_feature", "type": "number"},
            {
                "name": "text_feature_1",
                "type": "text",
                "encoder": {
                    "type": "rnn",
                    "activation": "sigmoid",
                },
            },
            {
                "name": "text_feature_2",
                "type": "text",
            },
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
        "defaults": {
            "number": {"preprocessing": {"missing_value_strategy": "drop_row"}, "encoder": {"type": "dense"}},
            "text": {
                "preprocessing": {
                    "missing_value_strategy": "drop_row",
                },
                "encoder": {
                    "type": "stacked_parallel_cnn",
                    "activation": "tanh",
                },
            },
        },
    }

    config_object = Config.from_dict(config)
    assert config_object.input_features.number_feature.preprocessing.missing_value_strategy == "drop_row"
    assert config_object.input_features.number_feature.encoder.type == "dense"

    assert config_object.input_features.text_feature_1.encoder.type == "rnn"
    assert config_object.input_features.text_feature_1.encoder.activation == "sigmoid"
    assert config_object.input_features.text_feature_1.preprocessing.missing_value_strategy == "drop_row"

    assert config_object.input_features.text_feature_2.encoder.type == "stacked_parallel_cnn"
    assert config_object.input_features.text_feature_2.encoder.activation == "tanh"
    assert config_object.input_features.text_feature_2.preprocessing.missing_value_strategy == "drop_row"


def test_config_object_to_config_dict():
    config = {
        "input_features": [
            {"name": "number_feature", "type": "number"},
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
    }

    config_object = Config.from_dict(config)
    config_dict = config_object.to_dict()

    assert INPUT_FEATURES in config_dict
    assert OUTPUT_FEATURES in config_dict
    assert PREPROCESSING in config_dict
    assert TRAINER in config_dict
    assert COMBINER in config_dict
    assert DEFAULTS in config_dict
    assert len(config_dict[DEFAULTS]) == 13
    assert HYPEROPT in config_dict


def test_update_config_object():
    config = {
        "input_features": [
            {"name": "text_feature", "type": "text"},
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
    }

    config_object = Config.from_dict(config)

    assert config_object.input_features.text_feature.encoder.type == "parallel_cnn"
    assert config_object.input_features.text_feature.encoder.max_sequence_length is None

    temp_config = {
        "input_features": [
            {"name": "text_feature", "type": "text", "encoder": {"type": "parallel_cnn", "max_sequence_length": 10}},
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
    }

    config_object.update_config_object(temp_config)

    assert config_object.input_features.text_feature.encoder.max_sequence_length == 10


def test_constructors():
    config = {
        "input_features": [
            {"name": "text_feature", "type": "text", "encoder": {"type": "parallel_cnn", "max_sequence_length": 10}},
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
    }

    config_obj = Config.from_dict(config)

    assert hasattr(config_obj, INPUT_FEATURES)
    assert hasattr(config_obj, OUTPUT_FEATURES)
    assert hasattr(config_obj, PREPROCESSING)
    assert hasattr(config_obj, TRAINER)
    assert hasattr(config_obj, COMBINER)
    assert hasattr(config_obj, DEFAULTS)
    assert hasattr(config_obj, HYPEROPT)

    with TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.yaml")
        with open(file_path, "w") as file:
            yaml.dump(config, file)

        config_obj = Config.from_yaml(file_path)

    assert hasattr(config_obj, INPUT_FEATURES)
    assert hasattr(config_obj, OUTPUT_FEATURES)
    assert hasattr(config_obj, PREPROCESSING)
    assert hasattr(config_obj, TRAINER)
    assert hasattr(config_obj, COMBINER)
    assert hasattr(config_obj, DEFAULTS)
    assert hasattr(config_obj, HYPEROPT)


def test_feature_enabling_disabling():
    config = {
        "input_features": [
            {"name": "text_feature", "type": "text"},
            {"name": "category_feature", "type": "number"}
        ],
        "output_features": [
            {
                "name": "number_output_feature",
                "type": "number",
            },
        ],
    }

    config_obj = Config.from_dict(config)

    assert config_obj.input_features.text_feature.active
    assert config_obj.input_features.category_feature.active

    config_obj.input_features.text_feature.disable()

    assert not config_obj.input_features.text_feature.active
