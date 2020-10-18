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
import yaml
import abc
from pathlib import Path
import pandas as pd

# define a default location for the cache
DEFAULT_CACHE_LOCATION = str(Path.home().joinpath('.ludwig_cache'))

PATH_HERE = os.path.abspath(os.path.dirname(__file__))


def read_config():
    config_path = os.path.join(PATH_HERE, "config/dataset_config.yaml")
    with open(config_path) as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


class BaseDataset:
    """Base class that defines the public interface for the ludwig dataset API.

    This includes the download, transform and converting the final transformed API
    into a resultant dataframe.
    """

    def __init__(self, dataset_name, cache_dir):
        self.name = dataset_name
        self.cache_dir = cache_dir or DEFAULT_CACHE_LOCATION

        config_full = read_config()
        self.config = config_full[dataset_name]
        self.version = self.config["version"]

    def download(self) -> None:
        """Download the file from config url that represents the raw unprocessed training data.

        The workflow for this involves unzipping the file and renaming it to raw.csv, which means
        keep trying to download the file till successful.
        """
        self.download_raw_dataset()

    def process(self) -> None:
        """Process the dataset to get it ready to be plugged into a dataframe.

        Converts into a format to be used by the ludwig training API. To do this we create
        a new dictionary that contains the KV pairs in the format that we need.
        """
        if not self.is_downloaded():
            self.download()
        self.process_downloaded_dataset()

    def load(self) -> pd.DataFrame:
        """Loads the processed data into a Pandas DataFrame."""
        if not self.is_processed():
            self.process()
        return self.load_processed_dataset()

    @property
    def raw_dataset_path(self):
        return os.path.join(self.download_dir, self.config["raw_path"])

    @property
    def processed_dataset_path(self):
        return os.path.join(self.download_dir, self.config["processed_path"])

    @property
    def download_dir(self):
        return os.path.join(self.cache_dir, f'{self.name}_{self.version}')

    @abc.abstractmethod
    def download_raw_dataset(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_downloaded_dataset(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_processed_dataset(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def is_downloaded(self) -> bool:
        """A helper method to verify the download.

        :returns: True or false identifying whether the file has been downloaded
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def is_processed(self) -> bool:
        """A helper method to verify that the processed file exists.

        :returns: True or false identifying whether the processed file exists
        """
        raise NotImplementedError()
