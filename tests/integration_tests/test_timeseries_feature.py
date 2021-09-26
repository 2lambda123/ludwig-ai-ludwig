import os
import shutil
import pytest
import pandas as pd

import torch

from ludwig.features.timeseries_feature import TimeseriesInputFeature
from tests.integration_tests.utils import timeseries_feature

BATCH_SIZE = 2
SEQ_SIZE = 10
DEFAULT_FC_SIZE = 256


@pytest.mark.parametrize(
    'enc_encoder',
    [
        'stacked_cnn', 'parallel_cnn', 'stacked_parallel_cnn', 'rnn', 'cnnrnn',
        'passthrough'
    ]
)
def test_timeseries_feature(enc_encoder):
    # synthetic timeseries tensor
    timeseries_tensor = torch.randn([BATCH_SIZE, SEQ_SIZE],
                                    dtype=torch.float32)

    # generate audio feature config
    timeseries_feature_config = timeseries_feature(
        encoder=enc_encoder,
        max_len=SEQ_SIZE,
        # simulated parameters determined by pre-processing
        max_sequence_length=SEQ_SIZE,
        embedding_size=1,
        should_embed=False
    )

    # instantiate audio input feature object
    timeseries_input_feature = TimeseriesInputFeature(timeseries_feature_config)

    # pass synthetic audio tensor through the audio input feature
    encoder_output = timeseries_input_feature(timeseries_tensor)

    # confirm correctness of the the audio encoder output
    assert isinstance(encoder_output, dict)
    assert 'encoder_output' in encoder_output
    assert isinstance(encoder_output['encoder_output'], torch.Tensor)
    if enc_encoder == 'passthrough':
        assert encoder_output['encoder_output'].shape \
               == (BATCH_SIZE, SEQ_SIZE, 1)
    else:
        assert encoder_output['encoder_output'].shape \
               == (BATCH_SIZE, DEFAULT_FC_SIZE)
