import logging

import ludwig
from ludwig.constants import DEFAULTS, INPUT_FEATURES, OUTPUT_FEATURES, PREPROCESSING, PROC_COLUMN, TYPE
from ludwig.data.cache.types import CacheableDataset
from ludwig.types import ModelConfigDict
from ludwig.utils.data_utils import hash_dict

logger = logging.getLogger(__name__)


def calculate_checksum(original_dataset: CacheableDataset, config: ModelConfigDict):
    """Calculates a checksum for a dataset and model config.

    The checksum is used to determine if the dataset and model config have changed since the last time the model was
    trained. If either has changed, a different checksum will be produced which will lead to a cache miss and force
    preprocessing to be performed again.
    """
    features = config.get(INPUT_FEATURES, []) + config.get(OUTPUT_FEATURES, []) + config.get("features", [])
    info = {
        "ludwig_version": ludwig.globals.LUDWIG_VERSION,
        "dataset_checksum": original_dataset.checksum,
        "global_preprocessing": config.get(PREPROCESSING, {}),
        "global_defaults": config.get(DEFAULTS, {}),
        # PROC_COLUMN contains both the feature name and the feature hash that is computed
        # based on each feature's preprocessing parameters and the feature's type.
        "feature_proc_columns": {feature[PROC_COLUMN] for feature in features},
        "feature_types": [feature[TYPE] for feature in features],
        "feature_preprocessing": [feature.get(PREPROCESSING, {}) for feature in features],
    }
    import pprint

    pprint.pprint(info)
    checksum = hash_dict(info, max_length=None).decode("ascii")
    logging.info(f"Checksum for dataset and model config: {checksum}")
    return checksum
