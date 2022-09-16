from marshmallow_dataclass import dataclass

from ludwig.constants import DROP_ROW, MISSING_VALUE_STRATEGY_OPTIONS, PREPROCESSING, TEXT
from ludwig.schema import utils as schema_utils
from ludwig.schema.features.preprocessing.base import BasePreprocessingConfig
from ludwig.schema.features.preprocessing.utils import register_preprocessor
from ludwig.schema.metadata.feature_metadata import FEATURE_METADATA
from ludwig.utils import strings_utils
from ludwig.utils.tokenizers import tokenizer_registry


@register_preprocessor(TEXT)
@dataclass
class TextPreprocessingConfig(BasePreprocessingConfig):
    """TextPreprocessingConfig is a dataclass that configures the parameters used for a text input feature."""

    pretrained_model_name_or_path: str = schema_utils.String(
        default=None,
        allow_none=True,
        description="This can be either the name of a pretrained HuggingFace model or a path where it was downloaded",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["pretrained_model_name_or_path"],
    )

    tokenizer: str = schema_utils.StringOptions(
        tokenizer_registry.keys(),
        default="space_punct",
        allow_none=False,
        description="Defines how to map from the raw string content of the dataset column to a sequence of elements.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["tokenizer"],
    )

    vocab_file: str = schema_utils.String(
        default=None,
        allow_none=True,
        description="Filepath string to a UTF-8 encoded file containing the sequence's vocabulary. On each line the "
        "first string until \t or \n is considered a word.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["vocab_file"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=256,
        allow_none=False,
        description="The maximum length (number of tokens) of the text. Texts that are longer than this value will be "
        "truncated, while texts that are shorter will be padded.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["max_sequence_length"],
    )

    most_common: int = schema_utils.PositiveInteger(
        default=20000,
        allow_none=False,
        description="The maximum number of most common tokens in the vocabulary. If the data contains more than this "
        "amount, the most infrequent symbols will be treated as unknown.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["most_common"],
    )

    padding_symbol: str = schema_utils.String(
        default=strings_utils.PADDING_SYMBOL,
        allow_none=False,
        description="The string used as the padding symbol for sequence features. Ignored for features using "
        "huggingface encoders, which have their own vocabulary.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["padding_symbol"],
    )

    unknown_symbol: str = schema_utils.String(
        default=strings_utils.UNKNOWN_SYMBOL,
        allow_none=False,
        description="The string used as the unknown symbol for sequence features. Ignored for features using "
        "huggingface encoders, which have their own vocabulary.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["unknown_symbol"],
    )

    padding: str = schema_utils.StringOptions(
        ["left", "right"],
        default="right",
        allow_none=False,
        description="the direction of the padding. right and left are available options.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["padding"],
    )

    lowercase: bool = schema_utils.Boolean(
        default=True,
        description="If true, converts the string to lowercase before tokenizing.",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["lowercase"],
    )

    missing_value_strategy: str = schema_utils.StringOptions(
        MISSING_VALUE_STRATEGY_OPTIONS,
        default="fill_with_const",
        allow_none=False,
        description="What strategy to follow when there's a missing value in a text column",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["missing_value_strategy"],
    )

    fill_value: str = schema_utils.String(
        default=strings_utils.UNKNOWN_SYMBOL,
        allow_none=False,
        description="The value to replace missing values with in case the missing_value_strategy is fill_with_const",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["fill_value"],
    )

    computed_fill_value: str = schema_utils.String(
        default=strings_utils.UNKNOWN_SYMBOL,
        allow_none=False,
        description="The internally computed fill value to replace missing values with in case the "
        "missing_value_strategy is fill_with_mode or fill_with_mean",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["computed_fill_value"],
    )


@register_preprocessor("text_output")
@dataclass
class TextOutputPreprocessingConfig(TextPreprocessingConfig):

    missing_value_strategy: str = schema_utils.StringOptions(
        MISSING_VALUE_STRATEGY_OPTIONS,
        default=DROP_ROW,
        allow_none=False,
        description="What strategy to follow when there's a missing value in a text output feature",
        parameter_metadata=FEATURE_METADATA[TEXT][PREPROCESSING]["missing_value_strategy"],
    )
