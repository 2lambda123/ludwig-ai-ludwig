from marshmallow_dataclass import dataclass

from ludwig.api_annotations import DeveloperAPI
from ludwig.constants import ACCURACY, CATEGORY, HITS_AT_K, LOSS, SOFTMAX_CROSS_ENTROPY
from ludwig.schema import utils as schema_utils
from ludwig.schema.decoders.base import BaseDecoderConfig
from ludwig.schema.decoders.utils import DecoderDataclassField
from ludwig.schema.encoders.base import BaseEncoderConfig
from ludwig.schema.encoders.utils import EncoderDataclassField
from ludwig.schema.features.base import BaseInputFeatureConfig, BaseOutputFeatureConfig
from ludwig.schema.features.loss.loss import BaseLossConfig
from ludwig.schema.features.loss.utils import LossDataclassField
from ludwig.schema.features.preprocessing.base import BasePreprocessingConfig
from ludwig.schema.features.preprocessing.utils import PreprocessingDataclassField
from ludwig.schema.features.utils import (
    ecd_input_config_registry,
    gbm_input_config_registry,
    input_mixin_registry,
    output_config_registry,
    output_mixin_registry,
)
from ludwig.schema.metadata.parameter_metadata import INTERNAL_ONLY
from ludwig.schema.utils import BaseMarshmallowConfig


@DeveloperAPI
@input_mixin_registry.register(CATEGORY)
@dataclass
class CategoryInputFeatureConfigMixin(BaseMarshmallowConfig):
    """CategoryInputFeatureConfigMixin is a dataclass that configures the parameters used in both the category
    input feature and the category global defaults section of the Ludwig Config."""

    preprocessing: BasePreprocessingConfig = PreprocessingDataclassField(feature_type=CATEGORY)


@DeveloperAPI
@ecd_input_config_registry.register(CATEGORY)
@dataclass
class ECDCategoryInputFeatureConfig(BaseInputFeatureConfig, CategoryInputFeatureConfigMixin):
    """CategoryInputFeatureConfig is a dataclass that configures the parameters used for a category input
    feature."""

    encoder: BaseEncoderConfig = EncoderDataclassField(
        feature_type=CATEGORY,
        default="dense",
    )


@DeveloperAPI
@gbm_input_config_registry.register(CATEGORY)
@dataclass
class GBMCategoryInputFeatureConfig(BaseInputFeatureConfig, CategoryInputFeatureConfigMixin):
    """CategoryInputFeatureConfig is a dataclass that configures the parameters used for a category input
    feature."""

    encoder: BaseEncoderConfig = EncoderDataclassField(
        feature_type=CATEGORY,
        default="passthrough",
    )


@DeveloperAPI
@output_mixin_registry.register(CATEGORY)
@dataclass
class CategoryOutputFeatureConfigMixin(BaseMarshmallowConfig):
    """CategoryOutputFeatureConfigMixin is a dataclass that configures the parameters used in both the category
    output feature and the category global defaults section of the Ludwig Config."""

    decoder: BaseDecoderConfig = DecoderDataclassField(
        feature_type=CATEGORY,
        default="classifier",
    )

    loss: BaseLossConfig = LossDataclassField(
        feature_type=CATEGORY,
        default=SOFTMAX_CROSS_ENTROPY,
    )


@DeveloperAPI
@output_config_registry.register(CATEGORY)
@dataclass(repr=False)
class CategoryOutputFeatureConfig(BaseOutputFeatureConfig, CategoryOutputFeatureConfigMixin):
    """CategoryOutputFeatureConfig is a dataclass that configures the parameters used for a category output
    feature."""

    calibration: bool = schema_utils.Boolean(
        default=False,
        description="Calibrate the model's output probabilities using temperature scaling.",
    )

    default_validation_metric: str = schema_utils.StringOptions(
        [ACCURACY],
        default=ACCURACY,
        description="Internal only use parameter: default validation metric for category output feature.",
        parameter_metadata=INTERNAL_ONLY,
    )

    dependencies: list = schema_utils.List(
        default=[],
        description="List of input features that this feature depends on.",
    )

    preprocessing: BasePreprocessingConfig = PreprocessingDataclassField(feature_type="category_output")

    reduce_dependencies: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the dependencies of the output feature.",
    )

    reduce_input: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce an input that is not a vector, but a matrix or a higher order tensor, on the first "
        "dimension (second if you count the batch dimension)",
    )

    top_k: int = schema_utils.NonNegativeInteger(
        default=3,
        description="Determines the parameter k, the number of categories to consider when computing the top_k "
        "measure. It computes accuracy but considering as a match if the true category appears in the "
        "first k predicted categories ranked by decoder's confidence.",
    )

    @staticmethod
    def get_output_metric_functions():
        return {LOSS: None, ACCURACY: None, HITS_AT_K: None}
