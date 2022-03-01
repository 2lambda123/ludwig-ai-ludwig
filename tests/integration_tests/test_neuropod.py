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
import itertools
import os
import shutil
import tempfile
from typing import List, Union

import numpy as np
import pandas as pd
import pytest
import torch

from ludwig.api import LudwigModel
from ludwig.constants import BINARY, LOGITS, NAME, PREDICTIONS, PROBABILITIES, SEQUENCE, SET, TEXT, TRAINER
from ludwig.utils.neuropod_utils import export_neuropod, generate_neuropod_torchscript
from ludwig.utils.strings_utils import str2bool
from tests.integration_tests.utils import (
    audio_feature,
    bag_feature,
    binary_feature,
    category_feature,
    date_feature,
    generate_data,
    h3_feature,
    image_feature,
    LocalTestBackend,
    number_feature,
    sequence_feature,
    set_feature,
    text_feature,
    timeseries_feature,
    vector_feature,
)


@pytest.mark.skip(reason="Issue #1451: Use torchscript.")
def test_neuropod(csv_filename):
    #######
    # Setup
    #######
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = tmpdir
        data_csv_path = os.path.join(tmpdir, csv_filename)
        image_dest_folder = os.path.join(tmpdir, "generated_images")
        audio_dest_folder = os.path.join(tmpdir, "generated_audio")

        input_features = [
            binary_feature(),
            number_feature(),
            category_feature(vocab_size=3),
            sequence_feature(vocab_size=3),
            text_feature(vocab_size=3),
            vector_feature(),
            image_feature(image_dest_folder),
            audio_feature(audio_dest_folder),
            timeseries_feature(),
            date_feature(),
            h3_feature(),
            set_feature(vocab_size=3),
            bag_feature(vocab_size=3),
        ]

        output_features = [
            binary_feature(),
            number_feature(),
            category_feature(vocab_size=3),
            sequence_feature(vocab_size=3),
            text_feature(vocab_size=3),
            set_feature(vocab_size=3),
            vector_feature(),
        ]

        # Generate test data
        data_csv_path = generate_data(input_features, output_features, data_csv_path)

        #############
        # Train model
        #############
        config = {"input_features": input_features, "output_features": output_features, TRAINER: {"epochs": 2}}
        ludwig_model = LudwigModel(config, backend=LocalTestBackend())
        ludwig_model.train(
            dataset=data_csv_path,
            skip_save_training_description=True,
            skip_save_training_statistics=True,
            skip_save_progress=True,
            skip_save_log=True,
            skip_save_processed_input=True,
            output_directory=dir_path,
        )

        data_df = pd.read_csv(data_csv_path)
        original_predictions_df, _ = ludwig_model.predict(dataset=data_df)

        ###################
        # save Ludwig model
        ###################
        ludwigmodel_path = os.path.join(dir_path, "ludwigmodel")
        shutil.rmtree(ludwigmodel_path, ignore_errors=True)
        ludwig_model.save(ludwigmodel_path)

        ################
        # build neuropod
        ################
        neuropod_path = os.path.join(dir_path, "neuropod")
        shutil.rmtree(neuropod_path, ignore_errors=True)
        export_neuropod(ludwigmodel_path, neuropod_path=neuropod_path, entrypoint="get_test_model")

        ########################
        # predict using neuropod
        ########################
        if_dict = {
            input_feature["name"]: np.expand_dims(
                np.array([str(x) for x in data_df[input_feature["name"]].tolist()], dtype="str"), 1
            )
            for input_feature in input_features
        }

        from neuropod.loader import load_neuropod

        neuropod_model = load_neuropod(neuropod_path, _always_use_native=False)
        preds = neuropod_model.infer(if_dict)

        for key in preds:
            preds[key] = np.squeeze(preds[key])

        #########
        # cleanup
        #########
        # Delete the temporary data created
        for path in [ludwigmodel_path, neuropod_path, image_dest_folder, audio_dest_folder]:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path, ignore_errors=True)

        ########
        # checks
        ########
        for output_feature in output_features:
            output_feature_name = output_feature["name"]
            output_feature_type = output_feature["type"]

            if (
                output_feature_name + "_predictions" in preds
                and output_feature_name + "_predictions" in original_predictions_df
            ):
                neuropod_pred = preds[output_feature_name + "_predictions"].tolist()
                if output_feature_type == BINARY:
                    neuropod_pred = [str2bool(x) for x in neuropod_pred]
                if output_feature_type in {SEQUENCE, TEXT, SET}:
                    neuropod_pred = [x.split() for x in neuropod_pred]

                original_pred = original_predictions_df[output_feature_name + "_predictions"].tolist()

                assert neuropod_pred == original_pred

            if (
                output_feature_name + "_probability" in preds
                and output_feature_name + "_probability" in original_predictions_df
            ):
                neuropod_prob = preds[output_feature_name + "_probability"].tolist()
                if output_feature_type in {SEQUENCE, TEXT, SET}:
                    neuropod_prob = [[float(n) for n in x.split()] for x in neuropod_prob]
                if any(isinstance(el, list) for el in neuropod_prob):
                    neuropod_prob = np.array(list(itertools.zip_longest(*neuropod_prob, fillvalue=0))).T

                original_prob = original_predictions_df[output_feature_name + "_probability"].tolist()
                if any(isinstance(el, list) for el in original_prob):
                    original_prob = np.array(list(itertools.zip_longest(*original_prob, fillvalue=0))).T

                assert np.allclose(neuropod_prob, original_prob)

            if (
                output_feature_name + "_probabilities" in preds
                and output_feature_name + "_probabilities" in original_predictions_df
            ):
                neuropod_prob = preds[output_feature_name + "_probabilities"].tolist()

                original_prob = original_predictions_df[output_feature_name + "_probabilities"].tolist()

                assert np.allclose(neuropod_prob, original_prob)


def test_neuropod_torchscript(csv_filename, tmpdir):
    data_csv_path = os.path.join(tmpdir, csv_filename)

    # Configure features to be tested:
    bin_str_feature = binary_feature()
    input_features = [
        bin_str_feature,
        # binary_feature(),
        number_feature(),
        category_feature(vocab_size=3),
        # TODO: future support
        # sequence_feature(vocab_size=3),
        # text_feature(vocab_size=3),
        # vector_feature(),
        # image_feature(image_dest_folder),
        # audio_feature(audio_dest_folder),
        # timeseries_feature(),
        # date_feature(),
        # h3_feature(),
        # set_feature(vocab_size=3),
        # bag_feature(vocab_size=3),
    ]
    output_features = [
        bin_str_feature,
        # binary_feature(),
        number_feature(),
        category_feature(vocab_size=3),
        # TODO: future support
        # sequence_feature(vocab_size=3),
        # text_feature(vocab_size=3),
        # set_feature(vocab_size=3),
        # vector_feature()
    ]
    backend = LocalTestBackend()
    config = {"input_features": input_features, "output_features": output_features, TRAINER: {"epochs": 2}}

    # Generate training data
    training_data_csv_path = generate_data(input_features, output_features, data_csv_path)

    # Convert bool values to strings, e.g., {'Yes', 'No'}
    df = pd.read_csv(training_data_csv_path)
    false_value, true_value = "No", "Yes"
    df[bin_str_feature[NAME]] = df[bin_str_feature[NAME]].map(lambda x: true_value if x else false_value)
    df.to_csv(training_data_csv_path)

    # Train Ludwig (Pythonic) model:
    ludwig_model = LudwigModel(config, backend=backend)
    ludwig_model.train(
        dataset=training_data_csv_path,
        skip_save_training_description=True,
        skip_save_training_statistics=True,
        skip_save_model=True,
        skip_save_progress=True,
        skip_save_log=True,
        skip_save_processed_input=True,
    )

    # Obtain predictions from Python model
    preds_dict, _ = ludwig_model.predict(dataset=training_data_csv_path, return_type=dict)

    # Create graph inference model (Torchscript) from trained Ludwig model.
    neuropod_module = generate_neuropod_torchscript(ludwig_model)

    def to_input(s: pd.Series) -> Union[List[str], torch.Tensor]:
        if s.dtype == "object":
            return s.to_list()
        return torch.from_numpy(s.to_numpy())

    df = pd.read_csv(training_data_csv_path)
    inputs = {name: to_input(df[feature.column]) for name, feature in ludwig_model.model.input_features.items()}
    outputs = neuropod_module(**inputs)

    # TODO: these are the only outputs we provide from Torchscript for now
    ts_outputs = {PREDICTIONS, PROBABILITIES, LOGITS}

    # Compare results from Python trained model against Torchscript
    for feature_name, feature_outputs_expected in preds_dict.items():
        assert feature_name in outputs

        feature_outputs = outputs[feature_name]
        for output_name, output_values_expected in feature_outputs_expected.items():
            if output_name not in ts_outputs:
                continue

            assert output_name in feature_outputs
            output_values = feature_outputs[output_name]
            if isinstance(output_values, list):
                # Strings should match exactly
                assert np.all(
                    output_values == output_values_expected
                ), f"feature: {feature_name}, output: {output_name}"
            else:
                assert np.allclose(
                    output_values, output_values_expected
                ), f"feature: {feature_name}, output: {output_name}"
