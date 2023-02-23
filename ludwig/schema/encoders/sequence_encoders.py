from typing import Any, Dict, List

from ludwig.api_annotations import DeveloperAPI
from ludwig.constants import AUDIO, SEQUENCE, TEXT, TIMESERIES
from ludwig.schema import common_fields, utils as schema_utils
from ludwig.schema.encoders.base import BaseEncoderConfig
from ludwig.schema.encoders.utils import register_encoder_config
from ludwig.schema.metadata import ENCODER_METADATA
from ludwig.schema.utils import ludwig_dataclass


@DeveloperAPI
@ludwig_dataclass
class SequenceEncoderConfig(BaseEncoderConfig):
    """Base class for sequence encoders."""

    def get_fixed_preprocessing_params(self) -> Dict[str, Any]:
        return {"cache_encoder_embeddings": False}


@DeveloperAPI
@register_encoder_config("passthrough", [TIMESERIES])
@ludwig_dataclass
class SequencePassthroughConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "SequencePassthrough"

    type: str = schema_utils.ProtectedString(
        "passthrough",
        description=ENCODER_METADATA["SequencePassthrough"]["type"].long_description,
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=256,
        description="The maximum length of a sequence.",
        parameter_metadata=ENCODER_METADATA["SequencePassthrough"]["max_sequence_length"],
    )

    encoding_size: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The size of the encoding vector, or None if sequence elements are scalars.",
        parameter_metadata=ENCODER_METADATA["SequencePassthrough"]["encoding_size"],
    )

    reduce_output: str = schema_utils.ReductionOptions(
        default=None,
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["SequencePassthrough"]["reduce_output"],
    )


@DeveloperAPI
@register_encoder_config("embed", [SEQUENCE, TEXT])
@ludwig_dataclass
class SequenceEmbedConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "SequenceEmbed"

    type: str = schema_utils.ProtectedString(
        "embed",
        description=ENCODER_METADATA["SequenceEmbed"]["type"].long_description,
    )

    dropout: float = common_fields.DropoutField(description="Dropout rate applied to the embedding.")

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Maximum sequence length past which tokenized sequence inputs will be truncated.",
        parameter_metadata=ENCODER_METADATA["SequenceEmbed"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description=(
            "Representation of the embedding. `dense` means the embeddings are initialized randomly, "
            "`sparse` means they are initialized to be one-hot encodings."
        ),
        parameter_metadata=ENCODER_METADATA["SequenceEmbed"]["representation"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary for the encoder",
        parameter_metadata=ENCODER_METADATA["SequenceEmbed"]["vocab"],
    )

    weights_initializer: str = common_fields.WeightsInitializerField(default="uniform")

    reduce_output: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["SequenceEmbed"]["reduce_output"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()


@DeveloperAPI
@register_encoder_config("parallel_cnn", [AUDIO, SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class ParallelCNNConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "ParallelCNN"

    type: str = schema_utils.ProtectedString(
        "parallel_cnn",
        description=ENCODER_METADATA["ParallelCNN"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="Dropout probability for the embedding.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["dropout"],
    )

    activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["activation"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The maximum length of all sequences",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description="Representation of the embedding.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["representation"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary for the encoder",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["vocab"],
    )

    num_conv_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel convolutional layers to use.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["num_conv_layers"],
    )

    conv_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for conv_layers
        default=None,
        description="List of dictionaries containing the parameters for each convolutional layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["conv_layers"],
    )

    num_filters: int = schema_utils.PositiveInteger(
        default=256,
        description="Number of filters, and by consequence number of output channels of the 1d convolution.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["num_filters"],
    )

    filter_size: int = schema_utils.PositiveInteger(
        default=3,
        description="Size of the 1d convolutional filter.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["filter_size"],
    )

    pool_function: str = schema_utils.ReductionOptions(
        default="max",
        description="Pooling function to use.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["pool_function"],
    )

    pool_size: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The default pool_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["pool_size"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="Whether to embed the input sequence.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["num_fc_layers"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["ParallelCNN"]["fc_layers"],
    )


@DeveloperAPI
@register_encoder_config("stacked_cnn", [AUDIO, SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class StackedCNNConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "StackedCNN"

    type: str = schema_utils.ProtectedString(
        "stacked_cnn",
        description=ENCODER_METADATA["StackedCNN"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="Dropout probability for the embedding.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["dropout"],
    )

    activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["activation"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The maximum length of all sequences",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description="Representation of the embedding.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["representation"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary for the encoder",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["vocab"],
    )

    num_conv_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel convolutional layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["num_conv_layers"],
    )

    conv_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for conv_layers
        default=None,
        description="List of dictionaries containing the parameters for each convolutional layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["conv_layers"],
    )

    num_filters: int = schema_utils.PositiveInteger(
        default=256,
        description="Number of filters, and by consequence number of output channels of the 1d convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["num_filters"],
    )

    filter_size: int = schema_utils.PositiveInteger(
        default=3,
        description="Size of the 1d convolutional filter.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["filter_size"],
    )

    strides: int = schema_utils.PositiveInteger(
        default=1,
        description="Stride length of the convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["strides"],
    )

    padding: str = schema_utils.StringOptions(
        ["valid", "same"],
        default="same",
        description="Padding to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["padding"],
    )

    dilation_rate: int = schema_utils.PositiveInteger(
        default=1,
        description="Dilation rate to use for dilated convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["dilation_rate"],
    )

    pool_function: str = schema_utils.ReductionOptions(
        default="max",
        description="Pooling function to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["pool_function"],
    )

    pool_size: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The default pool_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["pool_size"],
    )

    pool_strides: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Factor to scale down.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["pool_strides"],
    )

    pool_padding: str = schema_utils.StringOptions(
        ["valid", "same"],
        default="same",
        description="Padding to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["pool_padding"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="Whether to embed the input sequence.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["num_fc_layers"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNN"]["fc_layers"],
    )


@DeveloperAPI
@register_encoder_config("stacked_parallel_cnn", [AUDIO, SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class StackedParallelCNNConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "StackedParallelCNN"

    type: str = schema_utils.ProtectedString(
        "stacked_parallel_cnn",
        description=ENCODER_METADATA["StackedParallelCNN"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="Dropout probability for the embedding.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["dropout"],
    )

    activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["activation"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The maximum length of all sequences",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description="The representation of the embeddings. 'Dense' means the embeddings are initialized randomly. "
        "'Sparse' means they are initialized to be one-hot encodings.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["representation"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary of the input feature to encode",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["vocab"],
    )

    num_stacked_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="If stacked_layers is null, this is the number of elements in the stack of parallel convolutional "
        "layers. ",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["num_stacked_layers"],
    )

    stacked_layers: List[dict] = schema_utils.DictList(
        default=None,
        description="a nested list of lists of dictionaries containing the parameters of the stack of parallel "
        "convolutional layers. The length of the list determines the number of stacked parallel "
        "convolutional layers, length of the sub-lists determines the number of parallel conv layers and "
        "the content of each dictionary determines the parameters for a specific layer. ",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["stacked_layers"],
    )

    num_filters: int = schema_utils.PositiveInteger(
        default=256,
        description="Number of filters, and by consequence number of output channels of the 1d convolution.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["num_filters"],
    )

    filter_size: int = schema_utils.PositiveInteger(
        default=3,
        description="Size of the 1d convolutional filter.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["filter_size"],
    )

    pool_function: str = schema_utils.ReductionOptions(
        default="max",
        description="Pooling function to use.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["pool_function"],
    )

    pool_size: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The default pool_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["pool_size"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="If True the input sequence is expected to be made of integers and will be mapped into embeddings",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="sum",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["num_fc_layers"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedParallelCNN"]["fc_layers"],
    )


@DeveloperAPI
@register_encoder_config("rnn", [AUDIO, SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class StackedRNNConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "StackedRNN"

    type: str = schema_utils.ProtectedString(
        "rnn",
        description=ENCODER_METADATA["StackedRNN"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["dropout"],
    )

    recurrent_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for the recurrent state",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["recurrent_dropout"],
    )

    activation: str = schema_utils.ActivationOptions(
        default="tanh",
        description="The activation function to use",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["activation"],
    )

    recurrent_activation: str = schema_utils.ActivationOptions(
        default="sigmoid",
        description="The activation function to use in the recurrent step",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["recurrent_activation"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The maximum length of all sequences",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description="The representation of the embeddings. 'Dense' means the embeddings are initialized randomly. "
        "'Sparse' means they are initialized to be one-hot encodings.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["representation"],
    )

    cell_type: str = schema_utils.StringOptions(
        ["rnn", "lstm", "gru"],
        default="rnn",
        description="The type of recurrent cell to use. Available values are: `rnn`, `lstm`, `gru`. For reference "
        "about the differences between the cells please refer to PyTorch's documentation",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["cell_type"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary of the input feature to encode",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["vocab"],
    )

    num_layers: int = schema_utils.PositiveInteger(
        default=1,
        description="The number of stacked recurrent layers.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["num_layers"],
    )

    state_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The size of the state of the rnn.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["state_size"],
    )

    bidirectional: bool = schema_utils.Boolean(
        default=False,
        description="If true, two recurrent networks will perform encoding in the forward and backward direction and "
        "their outputs will be concatenated.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["bidirectional"],
    )

    unit_forget_bias: bool = schema_utils.Boolean(
        default=True,
        description="If true, add 1 to the bias of the forget gate at initialization",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["unit_forget_bias"],
    )

    recurrent_initializer: str = schema_utils.InitializerOptions(
        default="orthogonal",
        description="The initializer for recurrent matrix weights",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["recurrent_initializer"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="If True the input sequence is expected to be made of integers and will be mapped into embeddings",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="last",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.NonNegativeInteger(
        default=0,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["num_fc_layers"],
    )

    fc_activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["fc_activation"],
    )

    fc_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for fully connected layers",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["fc_dropout"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedRNN"]["fc_layers"],
    )


@DeveloperAPI
@register_encoder_config("cnnrnn", [AUDIO, SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class StackedCNNRNNConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "StackedCNNRNN"

    type: str = schema_utils.ProtectedString(
        "cnnrnn",
        description=ENCODER_METADATA["StackedCNNRNN"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["dropout"],
    )

    recurrent_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for the recurrent state",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["recurrent_dropout"],
    )

    conv_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for the convolutional layers",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["conv_dropout"],
    )

    activation: str = schema_utils.ActivationOptions(
        default="tanh",
        description="The activation function to use",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["activation"],
    )

    recurrent_activation: str = schema_utils.ActivationOptions(
        default="sigmoid",
        description="The activation function to use in the recurrent step",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["recurrent_activation"],
    )

    conv_activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each convolutional layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["conv_activation"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="The maximum length of all sequences",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        description="The representation of the embeddings. 'Dense' means the embeddings are initialized randomly. "
        "'Sparse' means they are initialized to be one-hot encodings.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["representation"],
    )

    cell_type: str = schema_utils.StringOptions(
        ["rnn", "lstm", "gru"],
        default="rnn",
        description="The type of recurrent cell to use. Available values are: `rnn`, `lstm`, `gru`. For reference "
        "about the differences between the cells please refer to PyTorch's documentation.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["cell_type"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary of the input feature to encode",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["vocab"],
    )

    num_filters: int = schema_utils.PositiveInteger(
        default=256,
        description="Number of filters, and by consequence number of output channels of the 1d convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["num_filters"],
    )

    filter_size: int = schema_utils.PositiveInteger(
        default=5,
        description="Size of the 1d convolutional filter.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["filter_size"],
    )

    strides: int = schema_utils.PositiveInteger(
        default=1,
        description="Stride length of the convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["strides"],
    )

    padding: str = schema_utils.StringOptions(
        ["valid", "same"],
        default="same",
        description="Padding to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["padding"],
    )

    dilation_rate: int = schema_utils.PositiveInteger(
        default=1,
        description="Dilation rate to use for dilated convolution.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["dilation_rate"],
    )

    pool_function: str = schema_utils.ReductionOptions(
        default="max",
        description="Pooling function to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["pool_function"],
    )

    pool_size: int = schema_utils.PositiveInteger(
        default=2,
        description="The default pool_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["pool_size"],
    )

    pool_strides: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Factor to scale down.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["pool_strides"],
    )

    pool_padding: str = schema_utils.StringOptions(
        ["valid", "same"],
        default="same",
        description="Padding to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["pool_padding"],
    )

    num_rec_layers: int = schema_utils.PositiveInteger(
        default=1,
        description="The number of stacked recurrent layers.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["num_rec_layers"],
    )

    state_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The size of the state of the rnn.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["state_size"],
    )

    bidirectional: bool = schema_utils.Boolean(
        default=False,
        description="If true, two recurrent networks will perform encoding in the forward and backward direction and "
        "their outputs will be concatenated.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["bidirectional"],
    )

    unit_forget_bias: bool = schema_utils.Boolean(
        default=True,
        description="If true, add 1 to the bias of the forget gate at initialization",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["unit_forget_bias"],
    )

    recurrent_initializer: str = schema_utils.InitializerOptions(
        default="orthogonal",
        description="The initializer for recurrent matrix weights",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["recurrent_initializer"],
    )

    num_conv_layers: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Number of parallel convolutional layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["num_conv_layers"],
    )

    conv_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for conv_layers
        default=None,
        description="List of dictionaries containing the parameters for each convolutional layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["conv_layers"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="If True the input sequence is expected to be made of integers and will be mapped into embeddings",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="last",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.NonNegativeInteger(
        default=0,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["num_fc_layers"],
    )

    fc_activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["fc_activation"],
    )

    fc_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for fully connected layers",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["fc_dropout"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedCNNRNN"]["fc_layers"],
    )


@DeveloperAPI
@register_encoder_config("transformer", [SEQUENCE, TEXT, TIMESERIES])
@ludwig_dataclass
class StackedTransformerConfig(SequenceEncoderConfig):
    @staticmethod
    def module_name():
        return "StackedTransformer"

    type: str = schema_utils.ProtectedString(
        "transformer",
        description=ENCODER_METADATA["StackedTransformer"]["type"].long_description,
    )

    dropout: float = schema_utils.FloatRange(
        default=0.1,
        min=0,
        max=1,
        description="The dropout rate for the transformer block",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["dropout"],
    )

    max_sequence_length: int = schema_utils.PositiveInteger(
        default=None,
        allow_none=True,
        description="Max length of all sequences",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["max_sequence_length"],
    )

    representation: str = schema_utils.StringOptions(
        ["dense", "sparse"],
        default="dense",
        allow_none=False,
        description="The representation of the embeddings. 'Dense' means the embeddings are initialized randomly. "
        "'Sparse' means they are initialized to be one-hot encodings.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["representation"],
    )

    vocab: list = schema_utils.List(
        default=None,
        description="Vocabulary of the input feature to encode",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["vocab"],
    )

    num_layers: int = schema_utils.PositiveInteger(
        default=1,
        description="The number of transformer layers.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["num_layers"],
    )

    hidden_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The size of the hidden representation within the transformer block. It is usually the same as "
        "the embedding_size, but if the two values are different, a projection layer will be added before "
        "the first transformer block.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["hidden_size"],
    )

    num_heads: int = schema_utils.PositiveInteger(
        default=8,
        description="Number of attention heads in each transformer block.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["num_heads"],
    )

    transformer_output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="Size of the fully connected layer after self attention in the transformer block. This is usually "
        "the same as hidden_size and embedding_size.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["transformer_output_size"],
    )

    use_bias: bool = schema_utils.Boolean(
        default=True,
        description="Whether to use a bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["use_bias"],
    )

    bias_initializer: str = schema_utils.InitializerOptions(
        default="zeros",
        description="Initializer to use for the bias vector.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["bias_initializer"],
    )

    weights_initializer: str = schema_utils.InitializerOptions(
        description="Initializer to use for the weights matrix.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["weights_initializer"],
    )

    should_embed: bool = schema_utils.Boolean(
        default=True,
        description="If True the input sequence is expected to be made of integers and will be mapped into embeddings",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["should_embed"],
    )

    embedding_size: int = common_fields.EmbeddingSize()

    embeddings_on_cpu: bool = common_fields.EmbeddingsOnCPU()

    embeddings_trainable: bool = common_fields.EmbeddingsTrainable()

    pretrained_embeddings: str = common_fields.PretrainedEmbeddings()

    reduce_output: str = schema_utils.ReductionOptions(
        default="last",
        description="How to reduce the output tensor along the `s` sequence length dimension if the rank of the "
        "tensor is greater than 2.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["reduce_output"],
    )

    output_size: int = schema_utils.PositiveInteger(
        default=256,
        description="The default output_size that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["output_size"],
    )

    norm: str = schema_utils.StringOptions(
        ["batch", "layer"],
        default=None,
        allow_none=True,
        description="The default norm that will be used for each layer.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["norm"],
    )

    norm_params: dict = schema_utils.Dict(
        default=None,
        description="Parameters used if norm is either `batch` or `layer`.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["norm_params"],
    )

    num_fc_layers: int = schema_utils.NonNegativeInteger(
        default=0,
        description="Number of parallel fully connected layers to use.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["num_fc_layers"],
    )

    fc_activation: str = schema_utils.ActivationOptions(
        description="The default activation function that will be used for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["fc_activation"],
    )

    fc_dropout: float = schema_utils.FloatRange(
        default=0.0,
        min=0,
        max=1,
        description="The dropout rate for fully connected layers",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["fc_dropout"],
    )

    fc_layers: List[dict] = schema_utils.DictList(  # TODO (Connor): Add nesting logic for fc_layers
        default=None,
        description="List of dictionaries containing the parameters for each fully connected layer.",
        parameter_metadata=ENCODER_METADATA["StackedTransformer"]["fc_layers"],
    )
