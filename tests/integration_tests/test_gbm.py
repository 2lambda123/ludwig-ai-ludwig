import contextlib
import os
import tempfile

import pytest

try:
    import ray as _ray
except ImportError:
    _ray = None
from marshmallow import ValidationError

from ludwig.api import LudwigModel
from ludwig.constants import MODEL_TYPE, TRAINER
from tests.integration_tests.utils import binary_feature, category_feature, generate_data, number_feature, text_feature


@contextlib.contextmanager
def ray_start(num_cpus=3, num_gpus=None):
    res = _ray.init(
        num_cpus=num_cpus,
        num_gpus=num_gpus,
        include_dashboard=False,
        object_store_memory=150 * 1024 * 1024,
    )
    try:
        yield res
    finally:
        _ray.shutdown()


@pytest.fixture(scope="module")
def local_backend():
    return {"type": "local"}


@pytest.fixture(scope="module")
def ray_backend():
    num_workers = 2
    num_cpus_per_worker = 1
    return {
        "type": "ray",
        "processor": {
            "parallelism": num_cpus_per_worker * num_workers,
        },
        "trainer": {
            "use_gpu": False,
            "num_workers": num_workers,
            "resources_per_worker": {
                "CPU": num_cpus_per_worker,
                "GPU": 0,
            },
        },
    }


def run_test_gbm_output_not_supported(backend_config):
    """Test that an error is raised when the output feature is not supported by the model."""
    input_features = [number_feature(), category_feature(reduce_output="sum")]
    output_features = [text_feature()]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_filename = os.path.join(tmpdir, "training.csv")
        dataset_filename = generate_data(input_features, output_features, csv_filename, num_examples=100)

        config = {MODEL_TYPE: "gbm", "input_features": input_features, "output_features": output_features}

        model = LudwigModel(config, backend=backend_config)
        with pytest.raises(
            ValueError, match="Model type GBM only supports numerical, categorical, or binary output features"
        ):
            model.train(dataset=dataset_filename, output_directory=tmpdir)


def test_local_gbm_output_not_supported(local_backend):
    run_test_gbm_output_not_supported(local_backend)


@pytest.mark.distributed
def test_ray_gbm_output_not_supported(ray_backend):
    with ray_start():
        run_test_gbm_output_not_supported(ray_backend)


def run_test_gbm_multiple_outputs(backend_config):
    """Test that an error is raised when the model is trained with multiple outputs."""
    input_features = [number_feature(), category_feature(reduce_output="sum")]
    output_features = [
        category_feature(vocab_size=3),
        binary_feature(),
        category_feature(vocab_size=3),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_filename = os.path.join(tmpdir, "training.csv")
        dataset_filename = generate_data(input_features, output_features, csv_filename, num_examples=100)

        config = {
            MODEL_TYPE: "gbm",
            "input_features": input_features,
            "output_features": output_features,
            TRAINER: {"num_boost_round": 2},
        }

        model = LudwigModel(config, backend=backend_config)
        with pytest.raises(ValueError, match="Only single task currently supported"):
            model.train(dataset=dataset_filename, output_directory=tmpdir)


def test_local_gbm_multiple_outputs(local_backend):
    run_test_gbm_multiple_outputs(local_backend)


@pytest.mark.distributed
def test_ray_gbm_multiple_outputs(ray_backend):
    with ray_start():
        run_test_gbm_multiple_outputs(ray_backend)


def run_test_gbm_binary(backend_config):
    """Test that the GBM model can train and predict a binary variable (binary classification)."""
    input_features = [number_feature(), category_feature(reduce_output="sum")]
    output_feature = binary_feature()
    output_features = [output_feature]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_filename = os.path.join(tmpdir, "training.csv")
        dataset_filename = generate_data(input_features, output_features, csv_filename, num_examples=100)

        config = {
            MODEL_TYPE: "gbm",
            "input_features": input_features,
            "output_features": output_features,
            TRAINER: {"num_boost_round": 2},
        }

        model = LudwigModel(config, backend=backend_config)
        _, _, output_directory = model.train(
            dataset=dataset_filename,
            output_directory=tmpdir,
            skip_save_processed_input=True,
            skip_save_progress=True,
            skip_save_unprocessed_output=True,
            skip_save_log=True,
        )
        model.load(os.path.join(tmpdir, "api_experiment_run", "model"))
        preds, _ = model.predict(dataset=dataset_filename, output_directory=output_directory)

    prob_col = preds[output_feature["name"] + "_probabilities"]
    if backend_config["type"] == "ray":
        prob_col = prob_col.compute()
    assert len(prob_col.iloc[0]) == 2
    assert prob_col.apply(sum).mean() == pytest.approx(1.0)


def test_local_gbm_binary(local_backend):
    run_test_gbm_binary(local_backend)


@pytest.mark.distributed
def test_ray_gbm_binary(ray_backend):
    with ray_start():
        run_test_gbm_binary(ray_backend)


def run_test_gbm_category(backend_config):
    """Test that the GBM model can train and predict a categorical output (multiclass classification)."""
    input_features = [number_feature(), category_feature(reduce_output="sum")]
    vocab_size = 3
    output_feature = category_feature(vocab_size=vocab_size)
    output_features = [output_feature]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_filename = os.path.join(tmpdir, "training.csv")
        dataset_filename = generate_data(input_features, output_features, csv_filename, num_examples=100)

        config = {
            MODEL_TYPE: "gbm",
            "input_features": input_features,
            "output_features": output_features,
            TRAINER: {"num_boost_round": 2},
        }

        model = LudwigModel(config, backend=backend_config)

        _, _, output_directory = model.train(
            dataset=dataset_filename,
            output_directory=tmpdir,
            skip_save_processed_input=True,
            skip_save_progress=True,
            skip_save_unprocessed_output=True,
            skip_save_log=True,
        )
        model.load(os.path.join(tmpdir, "api_experiment_run", "model"))
        preds, _ = model.predict(dataset=dataset_filename, output_directory=output_directory)

    prob_col = preds[output_feature["name"] + "_probabilities"]
    if backend_config["type"] == "ray":
        prob_col = prob_col.compute()
    assert len(prob_col.iloc[0]) == (vocab_size + 1)
    assert prob_col.apply(sum).mean() == pytest.approx(1.0)


def test_local_gbm_category(local_backend):
    run_test_gbm_category(local_backend)


@pytest.mark.distributed
def test_ray_gbm_category(ray_backend):
    with ray_start():
        run_test_gbm_category(ray_backend)


def run_test_gbm_number(backend_config):
    """Test that the GBM model can train and predict a numerical output (regression)."""
    # Given a dataset with a single input feature and a single output feature,
    input_features = [number_feature(), category_feature(reduce_output="sum")]
    output_feature = number_feature()
    output_features = [output_feature]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_filename = os.path.join(tmpdir, "training.csv")
        dataset_filename = generate_data(input_features, output_features, csv_filename, num_examples=100)

        config = {
            MODEL_TYPE: "gbm",
            "input_features": input_features,
            "output_features": output_features,
            TRAINER: {"num_boost_round": 2},
        }

        # When I train a model on the dataset, load the model from the output directory, and
        # predict on the dataset
        model = LudwigModel(config, backend=backend_config)

        model.train(
            dataset=dataset_filename,
            output_directory=tmpdir,
            skip_save_processed_input=True,
            skip_save_progress=True,
            skip_save_unprocessed_output=True,
            skip_save_log=True,
        )
        model.load(os.path.join(tmpdir, "api_experiment_run", "model"))
        preds, _ = model.predict(
            dataset=dataset_filename,
            output_directory=os.path.join(tmpdir, "predictions"),
        )

    # Then the predictions should be included in the output
    pred_col = preds[output_feature["name"] + "_predictions"]
    if backend_config["type"] == "ray":
        pred_col = pred_col.compute()
    assert pred_col.dtype == float


def test_local_gbm_number(local_backend):
    run_test_gbm_number(local_backend)


@pytest.mark.distributed
def test_ray_gbm_number(ray_backend):
    with ray_start():
        run_test_gbm_number(ray_backend)


def run_test_gbm_schema(backend_config):
    input_features = [number_feature()]
    output_features = [binary_feature()]

    # When I pass an invalid trainer configuration,
    invalid_trainer = "trainer"
    config = {
        MODEL_TYPE: "gbm",
        "input_features": input_features,
        "output_features": output_features,
        TRAINER: {
            "num_boost_round": 2,
            "type": invalid_trainer,
        },
    }
    with pytest.raises(ValidationError):
        # Then I should get a schema validation error
        LudwigModel(config, backend=backend_config)


def test_local_gbm_schema(local_backend):
    run_test_gbm_schema(local_backend)


@pytest.mark.distributed
def test_ray_gbm_schema(ray_backend):
    with ray_start():
        run_test_gbm_schema(ray_backend)
