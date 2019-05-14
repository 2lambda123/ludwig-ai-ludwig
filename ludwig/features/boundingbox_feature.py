#! /usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 Uber Technologies, Inc.
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
import logging
import os
from collections import OrderedDict

import numpy as np
import tensorflow as tf
from tensorflow.python.ops.losses.losses_impl import Reduction

from ludwig.constants import *
from ludwig.features.base_feature import BaseFeature
from ludwig.features.base_feature import InputFeature
from ludwig.features.base_feature import OutputFeature
from ludwig.models.modules.fully_connected_modules import fc_layer
from ludwig.models.modules.initializer_modules import get_initializer
from ludwig.models.modules.measure_modules import \
    absolute_error as get_absolute_error
from ludwig.models.modules.measure_modules import error as get_error
from ludwig.models.modules.measure_modules import r2 as get_r2
from ludwig.models.modules.measure_modules import \
    squared_error as get_squared_error
from ludwig.utils.misc import set_default_value



class BoundingBoxBaseFeature(BaseFeature):
    def __init__(self, feature):
        super().__init__(feature)
        self.type = NUMERICAL

    preprocessing_defaults = {
        'missing_value_strategy': FILL_WITH_CONST,
        'fill_value': 0
    }

    @staticmethod
    def get_feature_meta(column, preprocessing_parameters):
        return {}

    @staticmethod
    def add_feature_data(
            feature,
            dataset_df,
            data,
            metadata,
            preprocessing_parameters,
    ):
        data[feature['name']] = dataset_df[feature['name']].astype(
            np.float32).as_matrix()



class BoundingBoxOutputFeature(NumericalBaseFeature, OutputFeature):
    def __init__(self, feature):
        super().__init__(feature)

        self.loss = {'type': MEAN_SQUARED_ERROR}
        self.clip = None
        self.initializer = None
        self.regularize = True

        _ = self.overwrite_defaults(feature)

    def _get_output_placeholder(self):
        return tf.placeholder(
            tf.int64,
            [None],  # None is for dealing with variable batch size
            name='{}_placeholder'.format(self.name)
        )

    def _get_predictions(
            self,
            hidden,
            hidden_size,
            regularizer=None
    ):
    	pass

    def _get_loss(self, targets, predictions):
    	pass

    def _get_measures(self, targets, predictions):
    	pass

    def build_output(
            self,
            hidden,
            hidden_size,
            regularizer=None,
            **kwargs
    ):
    	pass

    @staticmethod
    def update_model_definition_with_metadata(
            output_feature,
            feature_metadata,
            *args,
            **kwargs
    ):
        pass

    @staticmethod
    def calculate_overall_stats(
            test_stats,
            output_feature,
            dataset,
            train_set_metadata
    ):
        pass

    @staticmethod
    def postprocess_results(
            output_feature,
            result,
            metadata,
            experiment_dir_name,
            skip_save_unprocessed_output=False
    ):
    	pass

    @staticmethod
    def populate_defaults(output_feature):
    	pass

