#! /usr/bin/env python
# coding=utf-8
# Copyright (c) 2020 Uber Technologies, Inc.
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
import json

from jsonschema import validate

from ludwig.combiners.combiners import combiner_registry
from ludwig.features.feature_registries import input_type_registry, output_type_registry

INPUT_FEATURE_TYPES = sorted(list(input_type_registry.keys()))
OUTPUT_FEATURE_TYPES = sorted(list(output_type_registry.keys()))
COMBINER_TYPES = sorted(list(combiner_registry.keys()))

def get_schema():
    schema = {
        'type': 'object',
        'properties': {
            'input_features': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'type': {'type': 'string', 'enum': INPUT_FEATURE_TYPES},
                        'column': {'type': 'string'},
                        'encoder': {'type': 'string'}
                    },
                    'allOf': get_input_encoder_conds() + get_input_preproc_conds(),
                    'required': ['name', 'type'],
                }
            },
            'output_features': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'type': {'type': 'string', 'enum': OUTPUT_FEATURE_TYPES},
                        'column': {'type': 'string'},
                        'decoder': {'type': 'string'}
                    },
                    'allOf': get_output_decoder_conds() + get_output_preproc_conds(),
                    'required': ['name', 'type'],
                }
            },
            'combiner': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string', 'enum': COMBINER_TYPES},
                },
                'allOf': get_combiner_conds(),
                'required': ['type'],
            },
            'training': {},
            'preprocessing': {},
            'hyperopt': {},
        },
        # 'definitions': get_custom_definitions(),
        'required': ['input_features', 'output_features']
    }
    return schema


def get_input_encoder_conds():
    conds = []
    for feature_type in INPUT_FEATURE_TYPES:
        feature_cls = input_type_registry[feature_type]
        encoder_names = list(feature_cls.encoder_registry.keys())
        encoder_cond = create_cond(
            {'type': feature_type},
            {'encoder': {'enum': encoder_names}},
        )
        conds.append(encoder_cond)
    return conds


def get_input_preproc_conds():
    conds = []
    for feature_type in INPUT_FEATURE_TYPES:
        feature_cls = input_type_registry[feature_type]
        preproc_spec = {
            'type': 'object',
            'properties': feature_cls.preprocessing_schema,
            'additionalProperties': False,
        }
        preproc_cond = create_cond(
            {'type': feature_type},
            {'preprocessing': preproc_spec},
        )
        conds.append(preproc_cond)
    return conds


def get_output_decoder_conds():
    conds = []
    for feature_type in OUTPUT_FEATURE_TYPES:
        feature_cls = output_type_registry[feature_type]
        decoder_names = list(feature_cls.decoder_registry.keys())
        decoder_cond = create_cond(
            {'type': feature_type},
            {'decoder': {'enum': decoder_names}},
        )
        conds.append(decoder_cond)
    return conds


def get_output_preproc_conds():
    conds = []
    for feature_type in OUTPUT_FEATURE_TYPES:
        feature_cls = output_type_registry[feature_type]
        preproc_spec = {
            'type': 'object',
            'properties': feature_cls.preprocessing_schema,
            'additionalProperties': False,
        }
        preproc_cond = create_cond(
            {'type': feature_type},
            {'preprocessing': preproc_spec},
        )
        conds.append(preproc_cond)
    return conds


def get_combiner_conds():
    conds = []
    for combiner_type in COMBINER_TYPES:
        combiner_cls = combiner_registry[combiner_type]
        # combiner_props = json.loads(combiner_cls.get_params_cls().schema_json())['properties']
        combiner_json = (combiner_cls
                         .get_marshmallow_schema_as_json()
                         ['definitions']
                         [combiner_cls.get_schema_cls().__name__]
                         ['properties'])
        combiner_cond = create_cond(
            {'type': combiner_type},
            combiner_json
        )
        conds.append(combiner_cond)
    return conds

def get_custom_definitions():
    pass
    # defs = {}
    # for combiner_type in COMBINER_TYPES:
    #     combiner_cls = combiner_registry[combiner_type]
    #     full_combiner_json = json.loads(combiner_cls.get_params_cls().schema_json())
    #     if 'definitions' in full_combiner_json:
    #         defs = {
    #             **defs,
    #             **full_combiner_json['definitions']
    #         }

    #         if hasattr(combiner_cls, "get_nullable_params"):
    #             nullableParams = combiner_cls.get_nullable_params()
    #             params_cls = combiner_cls.get_params_cls()

    #             for nparam in nullableParams:
    #                 nfield = params_cls.__fields__[nparam]
    #                 print(nfield)
    #                 path = nfield.type_.__name__
    #                 original_type = defs[path]["type"]
    #                 original_enum = defs[path]["enum"]
    #                 null = None
    #                 defs[path].update({"type": [null, original_type]})
    #                 defs[path].update({"enum": [null] + original_enum})
    #                 print(defs[path])
            # optionalParams = []
            # for param_name, field in params_cls.__fields__.items():
            #     if not field.required:
            #         optionalParams.append((param_name, field))
            # for param, field in optionalParams:
            #     print(param)
            #     print(field)
            #     print(field.name)
            #     print(field.type_)
            #     # if 'Enum' in field.type_.__name__:
            #     print(defs.keys())
            #     if 'Enum' in field.type_ and field.type_.__name__ in defs.keys():
            #         path = field.type_.__name__
            #         original_type = defs[path]["type"]
            #         defs[path].update({"type": ["null", original_type]})
            #         print(defs[path])
                # else:
                #     original_type = defs["properties"][param]["type"]
                #     schema["properties"][param].update({"type": ["null", original_type]})
    # return defs

def create_cond(if_pred, then_pred):
    return {
        'if': {
            'properties': {k: {'const': v} for k, v in if_pred.items()}
        },
        'then': {
            'properties': {k: v for k, v in then_pred.items()}
        }
    }


def validate_config(config):
    validate(instance=config, schema=get_schema())