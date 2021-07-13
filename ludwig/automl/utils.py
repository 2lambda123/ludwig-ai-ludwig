import logging
import sys
from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json
from pandas import Series

logger = logging.getLogger(__name__)


try:
    import ray
except ImportError:
    logger.error(
        ' ray is not installed. '
        'In order to use auto_train please run '
        'pip install ludwig[ray]'
    )
    sys.exit(-1)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FieldInfo:
    name: str
    dtype: str
    key: str = None
    distinct_values: int = 0
    nonnull_values: int = 0
    avg_words: int = None


def avg_num_tokens(field: Series) -> int:
    # sample a subset if dataframe is large
    if len(field) > 5000:
        field = field.sample(n=5000, random_state=40)
    unique_entries = field.unique()
    avg_words = Series(unique_entries).str.split().str.len().mean()
    return avg_words


def get_available_resources():
    # returns total number of gpus and cpus
    resources = ray.cluster_resources()
    gpus = resources.get('GPU', 0)
    cpus = resources.get('CPU', 0)
    resources = {
        'gpu': gpus,
        'cpu': cpus
    }
    return resources
