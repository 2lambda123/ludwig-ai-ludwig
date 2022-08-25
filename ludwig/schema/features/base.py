from typing import Any, Dict, List, Optional, Union

from marshmallow_dataclass import dataclass

from ludwig.constants import (
    AUDIO,
    BAG,
    BINARY,
    CATEGORY,
    DATE,
    H3,
    IMAGE,
    NUMBER,
    SEQUENCE,
    SET,
    TEXT,
    TIMESERIES,
    VECTOR,
)
from ludwig.schema import utils as schema_utils
from ludwig.schema.metadata.parameter_metadata import ParameterMetadata


@dataclass
class BaseFeatureConfig(schema_utils.BaseMarshmallowConfig):
    """Base class for feature configs."""

    name: str = schema_utils.String(
        allow_none=True,
        description="Name of the feature.",
    )

    type: str = schema_utils.StringOptions(
        allow_none=True,
        options=[AUDIO, BAG, BINARY, CATEGORY, DATE, H3, IMAGE, NUMBER, SEQUENCE, SET, TEXT, TIMESERIES, VECTOR],
        description="Type of the feature.",
    )

    column: str = schema_utils.String(
        allow_none=True,
        default=None,
        description="The column name of this feature. Defaults to name if not specified.",
    )

    proc_column: str = schema_utils.String(
        allow_none=True,
        default=None,
        description="The name of the preprocessed column name of this feature. Internal only.",
        parameter_metadata=ParameterMetadata(internal_only=True),
    )


@dataclass
class BaseInputFeatureConfig(BaseFeatureConfig):
    """Base input feature config class."""

    tied: str = schema_utils.String(
        default=None,
        allow_none=True,
        description="Name of input feature to tie the weights of the encoder with.  It needs to be the name of a "
        "feature of the same type and with the same encoder parameters.",
    )


@dataclass
class BaseOutputFeatureConfig(BaseFeatureConfig):
    """Base output feature config class."""

    reduce_input: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce an input that is not a vector, but a matrix or a higher order tensor, on the first "
        "dimension (second if you count the batch dimension)",
    )

    dependencies: List[str] = schema_utils.List(
        default=[],
        description="List of input features that this feature depends on.",
    )

    reduce_dependencies: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the dependencies of the output feature.",
    )

    input_size: int = schema_utils.PositiveInteger(
        default=None,
        description="Size of the input to the decoder.",
        parameter_metadata=ParameterMetadata(internal_only=True),
    )

    num_classes: int = schema_utils.PositiveInteger(
        default=None,
        description="Size of the input to the decoder.",
        parameter_metadata=ParameterMetadata(internal_only=True),
    )

    fc_layers: Optional[List[Dict[str, Any]]] = schema_utils.DictList(
        default=None, description="List of dictionaries containing the parameters for each fully connected layer."
    )

    num_fc_layers: int = schema_utils.NonNegativeInteger(
        default=0, description="Number of fully-connected layers if fc_layers not specified."
    )

    output_size: int = schema_utils.PositiveInteger(default=256, description="Output size of fully connected stack.")

    use_bias: bool = schema_utils.Boolean(default=True, description="Whether the layer uses a bias vector.")

    weights_initializer: Union[str, Dict] = schema_utils.InitializerOrDict(default="xavier_uniform", description="")

    bias_initializer: Union[str, Dict] = schema_utils.InitializerOrDict(default="zeros", description="")

    norm: Optional[str] = schema_utils.StringOptions(["batch", "layer"], description="")

    norm_params: Optional[dict] = schema_utils.Dict(description="")

    activation: str = schema_utils.ActivationOptions(default="relu", description="")

    dropout: float = schema_utils.FloatRange(default=0.0, min=0, max=1, description="")
