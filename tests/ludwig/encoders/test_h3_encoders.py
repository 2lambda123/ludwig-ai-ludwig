import logging

import torch

from ludwig.encoders import h3_encoders

logger = logging.getLogger(__name__)


def test_h3_embed():
    embed = h3_encoders.H3Embed()
    inputs = torch.tensor(
        [[2, 0, 14, 102, 7, 0, 3, 5, 0, 5, 5, 0, 5, 7, 7, 7, 7, 7, 7],
         [2, 0, 14, 102, 7, 0, 3, 5, 0, 5, 5, 0, 5, 7, 7, 7, 7, 7, 7]],
        dtype=torch.int32)
    outputs = embed(inputs)
    assert outputs['encoder_output'].size()[1:] == embed.output_shape


# def test_h3_weighted_sum():
#     embed = h3_encoders.H3WeightedSum()
#     inputs = torch.tensor([[2022, 6, 25, 5, 176, 9, 30, 59, 34259],
#                            [2022, 6, 25, 5, 176, 9, 30, 59, 34259]],
#                           dtype=torch.int32)
#     outputs = embed(inputs)
#     assert outputs['encoder_output'].size()[1:] == embed.output_shape
#
#
# def test_h3_rnn_embed():
#     date_embed = h3_encoders.H3RNNEmbed()
#     inputs = torch.tensor([[2022, 6, 25, 5, 176, 9, 30, 59, 34259],
#                            [2022, 6, 25, 5, 176, 9, 30, 59, 34259]],
#                           dtype=torch.int32)
#     outputs = date_embed(inputs)
#     assert outputs['encoder_output'].size()[1:] == embed.output_shape
