import logging
from typing import Tuple

import pytest
import torch

from ludwig.modules import reduction_modules

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@pytest.mark.parametrize("reduce_mode", ["last", "sum", "mean", "avg", "max", "concat", "attention", None])
@pytest.mark.parametrize("test_input_shape", [(16, 1, 4), (4, 10, 16)])
def test_sequence_reducer(reduce_mode: str, test_input_shape: Tuple[int, ...]):
    (batch_size, max_sequence_length, embedding_size) = test_input_shape
    sequence_reducer = reduction_modules.SequenceReducer(
        reduce_mode=reduce_mode,
        max_sequence_length=max_sequence_length,
        embedding_size=embedding_size).to(DEVICE)
    inputs = torch.zeros(test_input_shape)
    # Generates random sequence of random length for each instance in batch.
    for batch_index in range(batch_size):
        sequence_length = torch.randint(max_sequence_length, (1,))
        inputs[batch_index, :sequence_length] = torch.rand((sequence_length, embedding_size))
    outputs = sequence_reducer(inputs.to(DEVICE))
    assert outputs.shape[1:] == sequence_reducer.output_shape
