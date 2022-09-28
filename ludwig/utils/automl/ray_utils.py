import os

from ludwig.backend.ray import initialize_ray
from ludwig.utils.system_utils import Resources

try:
    import ray
except ImportError:
    raise ImportError(" ray is not installed. " "In order to use auto_train please run " "pip install ludwig[ray]")


def get_available_resources() -> Resources:
    # returns total number of gpus and cpus
    resources = ray.cluster_resources()
    return Resources(cpus=resources.get("CPU", 0), gpus=resources.get("GPU", 0))


def _ray_init():
    if ray.is_initialized():
        return

    # Forcibly terminate trial requested to stop after this amount of time passes
    os.environ.setdefault("TUNE_FORCE_TRIAL_CLEANUP_S", "120")

    initialize_ray()
