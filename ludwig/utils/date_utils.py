#! /usr/bin/env python
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
import time
from datetime import date, datetime
from typing import Union

import numpy as np

from ludwig.api_annotations import DeveloperAPI

SCALE_S = np.floor(np.log10(time.time()))


@DeveloperAPI
def create_vector_from_datetime_obj(datetime_obj):
    yearday = datetime_obj.toordinal() - date(datetime_obj.year, 1, 1).toordinal() + 1

    midnight = datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    second_of_day = (datetime_obj - midnight).seconds

    return [
        datetime_obj.year,
        datetime_obj.month,
        datetime_obj.day,
        datetime_obj.weekday(),
        yearday,
        datetime_obj.hour,
        datetime_obj.minute,
        datetime_obj.second,
        second_of_day,
    ]


@DeveloperAPI
def convert_number_to_datetime(timestamp: Union[float, int, str]) -> datetime:
    """Convert a numeric timestamp to a datetime object.

    `datetime` objects can be created from POSIX timestamps like those returned by `time.time()`.

    Args:
        timestamp: A numeric timestamp, e.g. a POSIX timestamp

    Returns:
        A datetime representation of `timestamp`.

    Raises:
        ValueError: Raised if `timestamp` is not a number or not a valid datetime.
    """
    try:
        timestamp = float(timestamp)
    except TypeError:
        raise ValueError(f"Provided value {timestamp} is not a valid numeric timestamp")

    # Determine the unit of the timestamp
    ts_scale = np.floor(np.log10(timestamp))

    # `datetime.datetime.fromtimestamp` expects a timestamp in seconds. Rescale the timestamp if it is not in seconds.
    if SCALE_S < ts_scale:
        delta = ts_scale - SCALE_S
        timestamp = timestamp / np.power(10, 3)
        print(f"\n\n\n\n\n\n\n\n{SCALE_S}, {ts_scale}, {delta}, {timestamp}\n\n\n\n\n\n\n\n")

    # Convert the timestamp to a datetime object. If it is not a valid timestamp, `ValueError` is raised.
    dt = datetime.fromtimestamp(timestamp)
    return dt
