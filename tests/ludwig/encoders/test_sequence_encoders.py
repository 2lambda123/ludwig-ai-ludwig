from typing import Type

import pytest
import torch

from ludwig.encoders.sequence_encoders import (
    ParallelCNN,
    SequenceEmbedEncoder,
    SequencePassthroughEncoder,
    StackedCNN,
    StackedCNNRNN,
    StackedParallelCNN,
    StackedRNN,
    StackedTransformer,
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@pytest.mark.parametrize("reduce_output", ["mean", "avg", "max", "last", "concat", "attention", None])
def test_sequence_passthrough_encoder(reduce_output: str):
    batch_size = 10
    sequence_length = 32
    sequence_passthrough_encoder = SequencePassthroughEncoder(
        reduce_output=reduce_output, max_sequence_length=sequence_length, encoding_size=8
    ).to(DEVICE)
    inputs = torch.rand(batch_size, sequence_length, 8).to(DEVICE)
    outputs = sequence_passthrough_encoder(inputs)
    # SequencePassthroughEncoder does not implement output_shape, expect output to match input shape after reduce.
    assert outputs["encoder_output"].shape[1:] == sequence_passthrough_encoder.reduce_sequence.output_shape


@pytest.mark.parametrize(
    "encoder_type",
    [SequenceEmbedEncoder, ParallelCNN, StackedCNN, StackedParallelCNN, StackedRNN, StackedCNNRNN, StackedTransformer],
)
@pytest.mark.parametrize("reduce_output", ["mean", "avg", "max", "last", "concat", "attention", None])
@pytest.mark.parametrize("vocab_size", [2, 1024])  # Uses vocabularies smaller than (and larger than) embedding size.
def test_sequence_encoders(encoder_type: Type, reduce_output: str, vocab_size: int):
    batch_size = 10
    sequence_length = 32
    sequence_embed_encoder = encoder_type(
        vocab=list(range(1, vocab_size + 1)), max_sequence_length=sequence_length, reduce_output=reduce_output
    ).to(DEVICE)
    inputs = torch.randint(2, (batch_size, sequence_length)).to(DEVICE)
    outputs = sequence_embed_encoder(inputs)
    assert outputs["encoder_output"].shape[1:] == sequence_embed_encoder.output_shape
