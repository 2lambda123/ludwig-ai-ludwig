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
import os

from ludwig.datasets.base_dataset import BaseDataset, DEFAULT_CACHE_LOCATION
from ludwig.datasets.mixins.download import ZipDownloadMixin

def load(cache_dir=DEFAULT_CACHE_LOCATION, split=False):
    dataset = Flickr8k(cache_dir=cache_dir)
    return dataset.load(split=split)

class Flickr8k(BaseDataset, ZipDownloadMixin):
    """The Flickr8k dataset.

    This pulls in an array of mixins for different types of functionality
    which belongs in the workflow for ingesting and transforming training data into a destination
    dataframe that can fit into Ludwig's training API.
    """

    def __init__(self, cache_dir=DEFAULT_CACHE_LOCATION):
        super().__init__(dataset_name="mnist", cache_dir=cache_dir)

    def download(self):
        super().download()
        print(f"downloaded raw dataset to {self.raw_dataset_path}")

    def process_downloaded_dataset(self):
        os.makedirs(self.processed_temp_path, exist_ok=True)
        print(f"created temp processed folder at {self.process_downloaded_dataset}")
        print("dataset processing not yet implemented")