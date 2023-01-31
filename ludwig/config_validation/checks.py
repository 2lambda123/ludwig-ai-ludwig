"""Checks that are not easily covered by marshmallow JSON schema validation like parameter interdependencies.

Assumes incoming configs are comprehensive (all parameters and defaults filled in), and has been schema-validated.
"""

from abc import ABC, abstractmethod

from ludwig.api_annotations import DeveloperAPI
from ludwig.config_validation.validation import check_schema
from ludwig.constants import (
    AUDIO,
    BACKEND,
    BINARY,
    CATEGORY,
    COMBINER,
    DECODER,
    ENCODER,
    IMAGE,
    IN_MEMORY,
    INPUT_FEATURES,
    MODEL_ECD,
    MODEL_GBM,
    MODEL_TYPE,
    NAME,
    NUMBER,
    OUTPUT_FEATURES,
    PREPROCESSING,
    SEQUENCE,
    SET,
    SPLIT,
    TEXT,
    TRAINER,
    TYPE,
    VECTOR,
)
from ludwig.decoders.registry import get_decoder_registry
from ludwig.encoders.registry import get_encoder_registry
from ludwig.error import ConfigValidationError
from ludwig.schema.combiners.utils import get_combiner_registry
from ludwig.schema.optimizers import optimizer_registry
from ludwig.types import ModelConfigDict
from ludwig.utils.metric_utils import get_feature_to_metric_names_map
from ludwig.utils.registry import Registry

# Set of all sequence feature types.
SEQUENCE_OUTPUT_FEATURE_TYPES = {SEQUENCE, TEXT, SET, VECTOR}

# Registry of configuration checks.
_config_checks = Registry()


@DeveloperAPI
def get_config_check_registry() -> Registry:
    return _config_checks


@DeveloperAPI
def register_config_check(description: str):
    def wrap(cls):
        get_config_check_registry()[description] = cls
        return cls

    return wrap


class ConfigCheck(ABC):
    """Checks instances of comprehensive (all parameters and defaults filled in) schema-validated config."""

    @staticmethod
    @abstractmethod
    def check(config: ModelConfigDict) -> None:
        """Checks config for validity."""
        raise NotImplementedError


def check_basic_required_parameters(config: ModelConfigDict) -> None:
    """Checks basic required parameters like that all features have names and types, and all types are valid."""
    # Check input features.
    for input_feature in config[INPUT_FEATURES]:
        if NAME not in input_feature:
            raise ConfigValidationError("All input features must have a name.")
        if TYPE not in input_feature:
            raise ConfigValidationError(f"Input feature {input_feature[NAME]} must have a type.")
        if ENCODER in input_feature:
            if (
                TYPE in input_feature[ENCODER]
                and input_feature[ENCODER][TYPE] not in get_encoder_registry()[input_feature[TYPE]]
            ):
                raise ConfigValidationError(
                    f"Encoder type '{input_feature[ENCODER][TYPE]}' for input feature {input_feature[NAME]} must be "
                    f"one of: {list(get_encoder_registry()[input_feature[TYPE]].keys())}."
                )

    # Check output features.
    for output_feature in config[OUTPUT_FEATURES]:
        if NAME not in output_feature:
            raise ConfigValidationError("All output features must have a name.")
        if TYPE not in output_feature:
            raise ConfigValidationError(f"Output feature {output_feature[NAME]} must have a type.")
        if output_feature[TYPE] not in get_decoder_registry():
            raise ConfigValidationError(
                f"Output feature {output_feature[NAME]} uses an invalid/unsupported output type "
                f"'{output_feature[TYPE]}'. Supported output features: {list(get_decoder_registry().keys())}."
            )
        if DECODER in output_feature:
            if (
                TYPE in output_feature[DECODER]
                and output_feature[DECODER][TYPE] not in get_decoder_registry()[output_feature[TYPE]]
            ):
                raise ConfigValidationError(
                    f"Decoder type for output feature {output_feature[NAME]} must be one of: "
                    f"{list(get_decoder_registry()[output_feature[TYPE]].keys())}."
                )

    # Check combiners.
    if config.get(MODEL_TYPE, MODEL_ECD) == MODEL_ECD:
        if COMBINER not in config:
            return
        if TYPE not in config[COMBINER]:
            raise ConfigValidationError("Combiner must have a type.")
        if config[COMBINER][TYPE] not in get_combiner_registry():
            raise ConfigValidationError(f"Combiner type must be one of: {list(get_combiner_registry().keys())}.")

    # Check trainer.
    if TRAINER in config and config[TRAINER] is None:
        raise ConfigValidationError("Trainer cannot be None.")

    # Check optimizer.
    if TRAINER in config and "optimizer" in config[TRAINER]:
        if config[TRAINER]["optimizer"] is None:
            raise ConfigValidationError("Trainer.optimizer cannot be None.")
        if TYPE in config[TRAINER]["optimizer"]:
            if config[TRAINER]["optimizer"][TYPE] not in optimizer_registry:
                raise ConfigValidationError(
                    f"Trainer.optimizer.type must be one of: {list(optimizer_registry.keys())}."
                )


@register_config_check("Checks that all feature names are unique.")
class CheckFeatureNamesUnique(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        input_features = config[INPUT_FEATURES]
        input_feature_names = {input_feature[NAME] for input_feature in input_features}

        output_features = config[OUTPUT_FEATURES]
        output_feature_names = {output_feature[NAME] for output_feature in output_features}

        if len(input_feature_names) + len(output_feature_names) != len(input_features) + len(output_features):
            raise ConfigValidationError("Feature names must be unique.")


@register_config_check("Checks that all tied features are valid.")
class CheckTiedFeaturesValid(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        input_features = config[INPUT_FEATURES]
        input_feature_names = {input_feature[NAME] for input_feature in input_features}

        for input_feature in input_features:
            if input_feature["tied"] and input_feature["tied"] not in input_feature_names:
                raise ConfigValidationError(
                    f"Feature {input_feature[NAME]} is tied to feature {input_feature['tied']}, but the "
                    f"'{input_feature['tied']}' feature does not exist."
                )


@register_config_check("Checks that checkpoints_per_epoch and steps_per_checkpoint aren't simultaneously defined.")
class CheckTrainingRunway(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[MODEL_TYPE] == MODEL_ECD:
            if config[TRAINER]["checkpoints_per_epoch"] != 0 and config[TRAINER]["steps_per_checkpoint"] != 0:
                raise ConfigValidationError(
                    "It is invalid to specify both trainer.checkpoints_per_epoch AND "
                    "trainer.steps_per_checkpoint. Please specify one or the other, or specify neither to "
                    "checkpoint/eval the model every epoch."
                )


@register_config_check("Checks that GBM model type isn't being used with the horovod backend.")
class CheckGBMHorovodIncompatibility(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if BACKEND not in config:
            return
        if config[MODEL_TYPE] == MODEL_GBM and config[BACKEND][TYPE] == "horovod":
            raise ConfigValidationError("Horovod backend does not support GBM models.")


@register_config_check("GBM models only support a single output feature.")
class CheckGBMSingleOutputFeature(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[MODEL_TYPE] == MODEL_GBM:
            if len(config[OUTPUT_FEATURES]) != 1:
                raise ConfigValidationError("GBM models only support a single output feature.")


@register_config_check("Checks that all input features for GBMs are of supported types.")
class CheckGBMFeatureTypes(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[MODEL_TYPE] == MODEL_GBM:
            for input_feature in config[INPUT_FEATURES]:
                if input_feature[TYPE] not in {BINARY, CATEGORY, NUMBER}:
                    raise ConfigValidationError(
                        "GBM Models currently only support Binary, Category, and Number features"
                    )


@register_config_check("Checks that in memory preprocessing is used with Ray backend.")
class CheckRayBackendInMemoryPreprocessing(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if BACKEND not in config:
            return

        if config[BACKEND][TYPE] == "ray" and not config[TRAINER][PREPROCESSING][IN_MEMORY]:
            raise ConfigValidationError(
                "RayBackend does not support lazy loading of data files at train time. "
                "Set preprocessing config `in_memory: True`"
            )

        for input_feature in config[INPUT_FEATURES]:
            if input_feature[TYPE] == AUDIO or input_feature[TYPE] == IMAGE:
                if not input_feature[PREPROCESSING][IN_MEMORY] and config[BACKEND][TYPE] != "ray":
                    raise ConfigValidationError(
                        "RayBackend does not support lazy loading of data files at train time. "
                        f"Set preprocessing config `in_memory: True` for input feature {input_feature[NAME]}"
                    )


@register_config_check("Checks that sequence concat combiner has at least one input feature that's sequential.")
class CheckSequenceConcatCombinerRequirements(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[MODEL_TYPE] != MODEL_ECD:
            return
        if config[COMBINER] != "sequence_concat":
            return
        has_sequence_input = False
        for input_feature in config[INPUT_FEATURES]:
            if input_feature[TYPE] in SEQUENCE_OUTPUT_FEATURE_TYPES:
                has_sequence_input = True
                break
        if not has_sequence_input:
            raise ConfigValidationError(
                "Sequence concat combiner should only be used for at least one sequential input feature."
            )


@register_config_check("Checks ComparatorCombiner requirements.")
class CheckComparatorCombinerRequirements(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        """All of the feature names for entity_1 and entity_2 are valid features."""
        if config[MODEL_TYPE] != MODEL_ECD:
            return
        if config[COMBINER] != "comparator":
            return

        input_feature_names = {input_feature[NAME] for input_feature in config[INPUT_FEATURES]}
        for entity in ["entity_1", "entity_2"]:
            for feature_name in config[COMBINER][entity]:
                if feature_name not in input_feature_names:
                    raise ConfigValidationError(
                        f"Feature {feature_name} in {entity} for the comparator combiner is not a valid "
                        "input feature name."
                    )


@register_config_check("Class balancing is only available for datasets with a single output feature.")
class CheckClassBalancePreprocessing(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[PREPROCESSING]["oversample_minority"] or config[PREPROCESSING]["undersample_majority"]:
            if len(config[OUTPUT_FEATURES]) != 1:
                raise ConfigValidationError(
                    "Class balancing is only available for datasets with a single output feature."
                )
            if config[OUTPUT_FEATURES][0][TYPE] != BINARY:
                raise ConfigValidationError("Class balancing is only supported for binary output features.")


@register_config_check("Oversample minority and undersample majority are mutually exclusive.")
class CheckSamplingExclusivity(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        if config[PREPROCESSING]["oversample_minority"] and config[PREPROCESSING]["undersample_majority"]:
            raise ConfigValidationError(
                "Oversample minority and undersample majority are mutually exclusive. Specify only one method."
            )


@register_config_check("Checks that the specified validation metric exists.")
class CheckValidationMetricExists(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        validation_metric_name = config[TRAINER]["validation_metric"]

        # Get all valid metrics.
        feature_to_metric_names_map = get_feature_to_metric_names_map(config[OUTPUT_FEATURES])
        all_valid_metrics = set()
        for metric_names in feature_to_metric_names_map.values():
            all_valid_metrics.update(metric_names)

        if validation_metric_name not in all_valid_metrics:
            raise ConfigValidationError(
                f"User-specified trainer.validation_metric '{validation_metric_name}' is not valid. "
                f"Available metrics are: {all_valid_metrics}"
            )


@register_config_check("Checks the validity of the splitter configuration.")
class CheckSplitter(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        from ludwig.data.split import get_splitter

        splitter = get_splitter(**config[PREPROCESSING][SPLIT])
        splitter.validate(config)


@register_config_check("Checks the schema.")
class CheckSchema(ConfigCheck):
    @staticmethod
    def check(config: ModelConfigDict) -> None:
        check_schema(config)
