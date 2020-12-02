# -*- coding: utf-8 -*-
# Copyright (c) 2020 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


import os

import mock
import numpy as np
import pandas as pd
import tensorflow as tf

from ludwig.api import LudwigModel
from ludwig.constants import NAME

from tests.integration_tests.utils import binary_feature, category_feature
from tests.integration_tests.utils import generate_data


def test_binary_predictions(tmpdir):
    input_features = [
        category_feature(vocab_size=3),
    ]

    feature = binary_feature()
    output_features = [
        feature,
    ]

    data_csv_path = generate_data(
        input_features,
        output_features,
        os.path.join(tmpdir, 'dataset.csv'),
    )
    data_df = pd.read_csv(data_csv_path)

    config = {
        'input_features': input_features,
        'output_features': output_features,
        'training': {'epochs': 1}
    }
    ludwig_model = LudwigModel(config)
    ludwig_model.train(
        dataset=data_df,
        output_directory=os.path.join(tmpdir, 'output'),
    )

    # Produce an even mix of True and False predictions, as the model may be biased towards
    # one direction without training
    def random_logits(*args, **kwargs):
        return tf.convert_to_tensor(
            np.random.uniform(low=-1.0, high=1.0, size=(len(data_df),))
        )

    with mock.patch('ludwig.features.binary_feature.BinaryOutputFeature.logits', random_logits):
        preds_df, _ = ludwig_model.predict(
            dataset=data_csv_path
        )

    cols = set(preds_df.columns)
    assert f'{feature[NAME]}_predictions' in cols
    assert f'{feature[NAME]}_probabilities_0' in cols
    assert f'{feature[NAME]}_probabilities_1' in cols
    assert f'{feature[NAME]}_probability' in cols

    for pred, prob_0, prob_1, prob in zip(
        preds_df[f'{feature[NAME]}_predictions'],
        preds_df[f'{feature[NAME]}_probabilities_0'],
        preds_df[f'{feature[NAME]}_probabilities_1'],
        preds_df[f'{feature[NAME]}_probability'],
    ):
        assert pred is True or pred is False
        if pred:
            assert prob_1 == prob
        else:
            assert prob_0 == prob
        assert prob_0 == 1 - prob_1
