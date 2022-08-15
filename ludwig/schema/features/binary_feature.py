from marshmallow_dataclass import dataclass
from typing import Union

from ludwig.utils import strings_utils

from ludwig.constants import BINARY, BINARY_WEIGHTED_CROSS_ENTROPY, MISSING_VALUE_STRATEGY_OPTIONS
from ludwig.schema import utils as schema_utils
from ludwig.schema.metadata.preprocessing_metadata import PREPROCESSING_METADATA
from ludwig.schema.decoders.base import BaseDecoderConfig
from ludwig.schema.decoders.utils import DecoderDataclassField
from ludwig.schema.encoders.base import BaseEncoderConfig
from ludwig.schema.encoders.utils import EncoderDataclassField
from ludwig.schema.features.base import BaseInputFeatureConfig, BaseOutputFeatureConfig, BasePreprocessingConfig
from ludwig.schema.features.utils import register_preprocessor, PreprocessingDataclassField


@register_preprocessor(BINARY)
@dataclass
class BinaryPreprocessingConfig(BasePreprocessingConfig):
    """BinaryPreprocessingConfig is a dataclass that configures the parameters used for a binary input feature."""

    missing_value_strategy: str = schema_utils.StringOptions(
        MISSING_VALUE_STRATEGY_OPTIONS + ["fill_with_false"],
        default="fill_with_false",
        allow_none=False,
        description="What strategy to follow when there's a missing value in a binary column",
    )

    fill_value: Union[int, float, str] = schema_utils.NumericOrStringOptionsField(
        strings_utils.all_bool_strs(),
        default=None,
        default_numeric=None,
        default_option=None,
        allow_none=False,
        min=0,
        max=1,
        description="The value to replace missing values with in case the missing_value_strategy is fill_with_const",
    )

    computed_fill_value: Union[int, float, str] = schema_utils.NumericOrStringOptionsField(
        strings_utils.all_bool_strs(),
        default=None,
        default_numeric=None,
        default_option=None,
        allow_none=False,
        min=0,
        max=1,
        description="The internally computed fill value to replace missing values with in case the "
        "missing_value_strategy is fill_with_mode or fill_with_mean",
        parameter_metadata=PREPROCESSING_METADATA["computed_fill_value"],
    )

    fallback_true_label: str = schema_utils.String(
        default=None,
        allow_none=True,
        description="The label to interpret as 1 (True) when the binary feature doesn't have a "
        "conventional boolean value",
    )


@dataclass
class BinaryInputFeatureConfig(BaseInputFeatureConfig):
    """BinaryInputFeatureConfig is a dataclass that configures the parameters used for a binary input feature."""

    preprocessing: BasePreprocessingConfig = PreprocessingDataclassField(feature_type=BINARY)

    encoder: BaseEncoderConfig = EncoderDataclassField(
        feature_type=BINARY,
        default="passthrough",
    )

    tied: str = schema_utils.String(
        default=None,
        allow_none=True,
        description="Name of input feature to tie the weights of the encoder with.  It needs to be the name of a "
        "feature of the same type and with the same encoder parameters.",
    )


@dataclass
class BinaryOutputFeatureConfig(BaseOutputFeatureConfig):
    """BinaryOutputFeatureConfig is a dataclass that configures the parameters used for a binary output feature."""

    loss: dict = schema_utils.Dict(  # TODO: Create schema for loss
        default={
            "type": BINARY_WEIGHTED_CROSS_ENTROPY,
            "robust_lambda": 0,
            "confidence_penalty": 0,
            "positive_class_weight": None,
            "weight": 1,
        },
        description="A dictionary containing a loss type and its hyper-parameters.",
    )

    decoder: BaseDecoderConfig = DecoderDataclassField(
        feature_type=BINARY,
        default="regressor",
    )

    reduce_input: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce an input that is not a vector, but a matrix or a higher order tensor, on the first "
        "dimension (second if you count the batch dimension)",
    )

    dependencies: list = schema_utils.List(
        default=[],
        description="List of input features that this feature depends on.",
    )

    reduce_dependencies: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the dependencies of the output feature.",
    )
