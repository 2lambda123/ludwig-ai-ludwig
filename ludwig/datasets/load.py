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

"""A class whose responsibility it is to take in a csv file and convert it into
any type of destination dataframe"""

import pandas as pd


class PandasLoadMixin:

    """This method converts a transformed data into a dataframe
    args:
    ret:
        The pandas dataframe"""
    def load_processed_dataset(self) -> pd.DataFrame:
        column_names = ["text", "class"]
        return pd.read_csv(self._processed_file_name, names=column_names)
