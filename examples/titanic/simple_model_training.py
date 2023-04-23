#!/usr/bin/env python

# # Simple Model Training Example
#
# This example is the API example for this Ludwig command line example
# (https://ludwig-ai.github.io/ludwig-docs/latest/examples/titanic/).

# Import required libraries
import logging
import os
import shutil

import yaml

from ludwig.api import LudwigModel

# from ludwig.datasets import titanic

# clean out prior results
shutil.rmtree("./results", ignore_errors=True)
# model_dir = "/src/results/simple_experiment_simple_model/model"

# Download and prepare the dataset
# training_set, test_set, _ = titanic.load(split=True)

config = yaml.safe_load(
    """
input_features:
    - name: Pclass
      type: category
    - name: Sex
      type: category
    - name: Age
      type: number
      preprocessing:
          missing_value_strategy: fill_with_mean
    - name: SibSp
      type: number
    - name: Parch
      type: number
    - name: Fare
      type: number
      preprocessing:
          missing_value_strategy: fill_with_mean
    - name: Embarked
      type: category

output_features:
    - name: Survived
      type: binary

trainer:
    batch_size: 64
    epochs: 10

backend:
    type: deepspeed
    zero_optimization:
        stage: 3
    # type: ray
    # trainer:
    #     strategy:
    #         type: deepspeed
    #         zero_optimization:
    #             stage: 3
    #     num_workers: 2
    #     use_gpu: True
    #     resources_per_worker:
    #         CPU: 1
    #         GPU: 1

"""
)

# Define Ludwig model object that drive model training
model = LudwigModel(config=config, logging_level=logging.INFO)

# initiate model training
(
    train_stats,  # dictionary containing training statistics
    preprocessed_data,  # tuple Ludwig Dataset objects of pre-processed training data
    output_directory,  # location of training results stored on disk
) = model.train(
    dataset="/home/ray/titanic.csv",
    experiment_name="simple_experiment",
    model_name="simple_model",
    # model_resume_path=model_dir,
)

# list contents of output directory
print("contents of output directory:", output_directory)
for item in os.listdir(output_directory):
    print("\t", item)

# batch prediction
# backend = {
#     "type": "ray",
#     "trainer": {
#         "strategy": {"type": "deepspeed", "zero_optimization": {"stage": 3}},
#         "num_workers": 2,
#         "use_gpu": True,
#         "resources_per_worker": {"CPU": 1, "GPU": 1},
#     },
# }
# backend = {
#     "type": "deepspeed",
#     "zero_optimization": {"stage": 3},
# }

# print(model_dir)
# model = LudwigModel.load(model_dir, backend=backend)
# results, _ = model.predict("/home/ray/titanic.csv", skip_save_predictions=False)
# print(results)
