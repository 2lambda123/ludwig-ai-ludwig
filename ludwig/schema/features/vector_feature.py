from marshmallow_dataclass import dataclass

from ludwig.constants import MISSING_VALUE_STRATEGY_OPTIONS

from ludwig.constants import VECTOR, MEAN_SQUARED_ERROR
from ludwig.schema import utils as schema_utils
from ludwig.schema.metadata.preprocessing_metadata import PREPROCESSING_METADATA
from ludwig.schema.decoders.base import BaseDecoderConfig
from ludwig.schema.decoders.utils import DecoderDataclassField
from ludwig.schema.encoders.base import BaseEncoderConfig
from ludwig.schema.encoders.utils import EncoderDataclassField
from ludwig.schema.features.base import BaseInputFeatureConfig, BaseOutputFeatureConfig, BasePreprocessingConfig
from ludwig.schema.features.utils import register_preprocessor
from ludwig.schema.preprocessing import PreprocessingDataclassField


@dataclass
class VectorInputFeatureConfig(BaseInputFeatureConfig):
    """VectorInputFeatureConfig is a dataclass that configures the parameters used for a vector input feature."""

    preprocessing: BasePreprocessingConfig = PreprocessingDataclassField(feature_type=VECTOR)

    encoder: BaseEncoderConfig = EncoderDataclassField(
        feature_type=VECTOR,
        default="dense",
    )


@dataclass
class VectorOutputFeatureConfig(BaseOutputFeatureConfig):
    """VectorOutputFeatureConfig is a dataclass that configures the parameters used for a vector output feature."""

    reduce_input: str = schema_utils.ReductionOptions(
        default=None,
        description="How to reduce an input that is not a vector, but a matrix or a higher order tensor, on the first "
                    "dimension (second if you count the batch dimension)",
    )

    reduce_dependencies: str = schema_utils.ReductionOptions(
        default=None,
        description="How to reduce the dependencies of the output feature.",
    )

    loss: dict = schema_utils.Dict(
        default={
            "type": MEAN_SQUARED_ERROR,
            "weight": 1,
        },
        description="A dictionary containing a loss type and its hyper-parameters.",
    )

    decoder: BaseDecoderConfig = DecoderDataclassField(
        feature_type=VECTOR,
        default="projector",
    )


@register_preprocessor(VECTOR)
@dataclass
class VectorPreprocessingConfig(BasePreprocessingConfig):

    vector_size: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The size of the vector. If None, the vector size will be inferred from the data.",
    )

    missing_value_strategy: str = schema_utils.StringOptions(
        MISSING_VALUE_STRATEGY_OPTIONS,
        default="fill_with_const",
        allow_none=False,
        description="What strategy to follow when there's a missing value in a vector column",
    )

    fill_value: str = schema_utils.String(
        default="",
        allow_none=False,
        pattern=r"^([0-9]+(\.[0-9]*)?\s*)*$",
        description="The value to replace missing values with in case the missing_value_strategy is fill_with_const",
    )

    computed_fill_value: str = schema_utils.String(
        default="",
        allow_none=False,
        pattern=r"^([0-9]+(\.[0-9]*)?\s*)*$",
        description="The internally computed fill value to replace missing values with in case the "
        "missing_value_strategy is fill_with_mode or fill_with_mean",
        parameter_metadata=PREPROCESSING_METADATA["computed_fill_value"],
    )
