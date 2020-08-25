import logging

import pytest

import tensorflow as tf

from ludwig.features.numerical_feature import NumericalOutputFeature
from ludwig.modules.reduction_modules import reduce_mode_registry
from tests.integration_tests.utils import numerical_feature


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("ludwig").setLevel(logging.INFO)

BATCH_SIZE = 16
SEQ_SIZE = 12
HIDDEN_SIZE = 128
OTHER_HIDDEN_SIZE = 32
OTHER_HIDDEN_SIZE2 = 18


# unit test for dependency concatenation
# tests both single and multiple dependencies
@pytest.mark.parametrize(
    'dependent_hidden_shape2', [
        None,
        [BATCH_SIZE, OTHER_HIDDEN_SIZE2],
        [BATCH_SIZE, SEQ_SIZE, OTHER_HIDDEN_SIZE2]

    ]
)
@pytest.mark.parametrize(
    'dependent_hidden_shape', [
        [BATCH_SIZE, OTHER_HIDDEN_SIZE],
        [BATCH_SIZE, SEQ_SIZE, OTHER_HIDDEN_SIZE]

    ]
)
@pytest.mark.parametrize(
    'hidden_shape', [
        [BATCH_SIZE, HIDDEN_SIZE],
        [BATCH_SIZE, SEQ_SIZE, HIDDEN_SIZE]
    ]
)
@pytest.mark.parametrize(
    'reduce_dependencies', ['sum', 'mean', 'avg', 'max', 'concat', 'last']
)
def test_multiple_dependencies(
        reduce_dependencies,
        hidden_shape,
        dependent_hidden_shape,
        dependent_hidden_shape2
):

    # setup at least for a single dependency
    hidden_layer = tf.random.normal(
        hidden_shape,
        dtype=tf.float32
    )
    other_hidden_layer = tf.random.normal(
        dependent_hidden_shape,
        dtype=tf.float32
    )
    other_dependencies = {
        'feature_name': other_hidden_layer,
    }

    # setup dummy output feature to be root of dependency list
    num_feature_defn = numerical_feature()
    num_feature_defn['loss'] = {'type': 'mean_squared_error'}
    num_feature_defn['dependencies'] = ['feature_name']
    if len(dependent_hidden_shape) > 2:
        num_feature_defn['reduce_dependencies'] = reduce_dependencies

    # Based on specification calculate expected resulting hidden size for
    # with one dependencies
    if reduce_dependencies == 'concat' and len(hidden_shape) == 2 and \
            len(dependent_hidden_shape) == 3:
            expected_hidden_size = HIDDEN_SIZE + OTHER_HIDDEN_SIZE * SEQ_SIZE
    else:
        expected_hidden_size = HIDDEN_SIZE + OTHER_HIDDEN_SIZE

    # set up if multiple dependencies specified, setup second depdendent feature
    if dependent_hidden_shape2:
        other_hidden_layer2 = tf.random.normal(
            dependent_hidden_shape2,
            dtype=tf.float32
        )
        other_dependencies['feature_name2'] = other_hidden_layer2
        num_feature_defn['dependencies'].append('feature_name2')
        if len(dependent_hidden_shape2) > 2:
            num_feature_defn['reduce_dependencies'] = reduce_dependencies

        # Based on specification calculate marginal increase in resulting
        # hidden size with two dependencies
        if reduce_dependencies == 'concat' and len(hidden_shape) == 2 and \
                len(dependent_hidden_shape2) == 3:
                expected_hidden_size += OTHER_HIDDEN_SIZE2 * SEQ_SIZE
        else:
            expected_hidden_size += OTHER_HIDDEN_SIZE2

    # test dependency concatenation
    out_feature = NumericalOutputFeature(num_feature_defn)
    results = out_feature.concat_dependencies(
        hidden_layer,
        other_dependencies
    )

    # confirm size of resutling concat_dependencies() call
    if len(hidden_shape) > 2:
        assert results.shape.as_list() == \
               [BATCH_SIZE, SEQ_SIZE, expected_hidden_size]
    else:
        assert results.shape.as_list() == [BATCH_SIZE, expected_hidden_size]



