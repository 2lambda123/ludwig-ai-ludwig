import pytest
from marshmallow import ValidationError

from ludwig.config_validation.validation import validate_config
from tests.integration_tests.utils import binary_feature, category_feature, number_feature, text_feature


def test_config_input_output_features():
    config = {
        "input_features": [
            category_feature(encoder={"type": "dense"}),
            number_feature(encoder={"type": "passthrough"}),
        ],
        "output_features": [binary_feature(decoder={"type": "regressor"})],
    }

    validate_config(config)


def test_incorrect_input_features_config():
    config = {
        "input_features": [
            category_feature(preprocessing={"normalization": "zscore"}),
        ],
        "output_features": [binary_feature()],
    }

    # TODO(ksbrar): Circle back after discussing whether additional properties should be allowed long-term.
    # # Not a preprocessing param for category feature
    # with pytest.raises(ValidationError):
    #     validate_config(config)

    config = {
        "input_features": [
            text_feature(preprocessing={"padding_symbol": 0}),
        ],
        "output_features": [binary_feature()],
    }

    # Incorrect type for padding_symbol preprocessing param
    with pytest.raises(ValidationError):
        validate_config(config)

    config = {
        "input_features": [
            binary_feature(),
        ],
        "output_features": [binary_feature()],
    }
    del config["input_features"][0]["type"]

    # Incorrect type for padding_symbol preprocessing param
    with pytest.raises(ValidationError):
        validate_config(config)


def test_incorrect_output_features_config():
    config = {
        "input_features": [
            number_feature(),
        ],
        "output_features": [binary_feature(decoder="classifier")],
    }

    # Invalid decoder for binary output feature
    with pytest.raises(ValidationError):
        validate_config(config)


def test_too_few_features_config():
    ifeatures = [number_feature()]
    ofeatures = [binary_feature()]

    validate_config(
        {
            "input_features": ifeatures,
            "output_features": ofeatures,
        }
    )

    # Must have at least one input feature
    with pytest.raises(ValidationError, match=r"Error: \[\] is too short"):
        validate_config(
            {
                "input_features": [],
                "output_features": ofeatures,
            }
        )

    # Must have at least one output feature
    with pytest.raises(ValidationError, match=r"Error: \[\] is too short"):
        validate_config(
            {
                "input_features": ifeatures,
                "output_features": [],
            }
        )


def test_too_many_features_config():
    # GBMs Must have exactly one output feature
    with pytest.raises(ValidationError, match=r"Error: .* is too long"):
        validate_config(
            {
                "input_features": [number_feature()],
                "output_features": [binary_feature(), number_feature()],
                "model_type": "gbm",
            }
        )

    # Multi-output is fine for ECD
    validate_config(
        {
            "input_features": [number_feature()],
            "output_features": [binary_feature(), number_feature()],
            "model_type": "ecd",
        }
    )