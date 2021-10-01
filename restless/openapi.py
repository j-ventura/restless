import json

import yaml
from restless import Handler
from datetime import datetime
from collections import Hashable
from inspect import _empty
from restless.parameters import BinaryParameter
from restless.security import Security
from typing import List, Union
from restless.util import snake_to_camel

OPENAPI = "3.0.0"

TYPE_MAPPING = {
    str: "string",
    bool: "boolean",
    bytes: "file",
    datetime: "string",
    set: "array",
    int: "integer",
    float: "number",
    list: "array",
    dict: "object"
}


def make_security(security: List[Union[List[str], str]], spec: dict):
    for sec in security or []:
        if isinstance(sec, str):
            assert sec in spec['components']['securitySchemes'], spec['components']['securitySchemes']
        else:
            for s in sec:
                assert s in spec['components']['securitySchemes']

    return [
        {sec: []} if isinstance(sec, str) else {s: [] for s in sec}
        for sec in security
    ]


def get_handlers(handlers):
    if isinstance(handlers, dict):
        for v in handlers.values():
            for found in get_handlers(v):
                yield found

    else:
        yield handlers


def make_spec(
        title,
        description,
        version,
        api_handler: Handler,
        file_name='spec.yaml',
        servers=None,
        security: List[Security] = None,
        default_security: List[Union[List[str], str]] = None,
        data_format=None
):
    spec = {
        'openapi': OPENAPI,
        'tags': [],
        'info': {
            'title': title,
            'description': description,
            'version': version
        },
        'paths': {},
        'servers': servers or [],
        'components': {
            'securitySchemes': {
                sec.name: dict(sec) for sec in (security or [])
            },
            'schemas': {
                'Error': {
                    'properties': {
                        'error': {
                            'type': 'string'
                        },
                        'details': {
                            'type': 'object'
                        }
                    },
                    'required': [
                        'error'
                    ]
                }
            }
        }
    }

    if default_security:
        spec['security'] = make_security(default_security, spec)

    for sec in default_security or []:
        if isinstance(sec, str):
            assert sec in spec['components']['securitySchemes'], spec['components']['securitySchemes']
        else:
            for s in sec:
                assert s in spec['components']['securitySchemes']

    for handler in get_handlers(api_handler.handlers):
        if handler.path not in spec['paths']:
            spec['paths'][handler.path] = {}

        target = spec['paths'][handler.path]

        if handler.http_method not in target:
            target[handler.http_method] = {}

        target = target[handler.http_method]

        if handler.security is not None:
            if handler.security:
                target['security'] = make_security(handler.security, spec)
        else:
            target['security'] = []

        target['description'] = handler.method.__doc__ or handler.method.__name__
        target['responses'] = {
            code: {
                'description': description,
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Error'
                        }
                    }
                }
            }
            for code, description in [
                ('400', 'Bad Request'),
                ('401', 'Unauthorized'),
                ('403', 'Forbidden'),
                ('404', 'Not Found')
            ]
        }
        target['parameters'] = []

        if handler.tags:
            target['tags'] = handler.tags
        else:
            tokens = handler.path.split('/')

            if len(tokens) > 1:
                target['tags'] = [tokens[1]]
            else:
                target['tags'] = ['default']

        returns = handler.sig.return_annotation if isinstance(handler.sig.return_annotation, dict) else {}

        for code, model in returns.items():
            if isinstance(model, list):
                schema = {
                    "type": "array",
                    "items": {}
                }

                t = schema['items']
                model = model[0]
            else:
                schema = {}
                t = schema

            if isinstance(model, Hashable) and model in TYPE_MAPPING:
                t['type'] = TYPE_MAPPING[model]
            elif hasattr(model, 'schema'):
                t['$ref'] = '#/components/schemas/' + model.__name__
                spec['components']['schemas'][model.__name__] = model.schema()

                if api_handler.use_camel_case:
                    spec['components']['schemas'][model.__name__] = snake_to_camel(
                        spec['components']['schemas'][model.__name__]
                    )

            target['responses'][str(code)] = {
                'description': description,
                'content': {
                    'application/json': {
                        'schema': schema
                    }
                }
            }

        for param, model in handler.parameters.items():
            if getattr(model, "LOCATION", "body") not in ['body', 'formData']:
                param_spec = {
                    'name': snake_to_camel(param) if api_handler.use_camel_case else param,
                    'in': getattr(model, "LOCATION", "body"),
                    'required': handler.sig.parameters[param].default == _empty,
                    'description': model.__doc__ or param,
                    'schema': {
                        'type': 'string'
                    }
                }

                target['parameters'].append(param_spec)
            else:
                if 'requestBody' not in target:
                    target['requestBody'] = {"content": {}}

                if hasattr(model, 'schema'):
                    spec['components']['schemas'][model.__name__] = model.schema()

                    if api_handler.use_camel_case:
                        spec['components']['schemas'][model.__name__] = snake_to_camel(
                            spec['components']['schemas'][model.__name__]
                        )

                    target['requestBody']['content']['application/json'] = {
                        'schema': {
                            '$ref': '#/components/schemas/' + model.__name__
                        }
                    }

                elif issubclass(model, BinaryParameter):
                    target['requestBody']['content']['application/octet-stream'] = {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }

                elif getattr(model, "LOCATION", "body") == "formData":
                    if 'multipart/form-data' not in target['requestBody']['content']:
                        target['requestBody']['content']['multipart/form-data'] = {
                            'schema': {
                                'type': 'object',
                                'properties': {}
                            }
                        }

                    if issubclass(model, str):
                        target['requestBody']['content']['multipart/form-data']['schema']['properties'][param] = {
                            'type': 'string'
                        }

                    else:
                        target['requestBody']['content']['multipart/form-data']['schema']['properties'][param] = {
                            'type': 'string',
                            'format': 'binary'
                        }

    data_format = data_format or file_name.split('.')[1]

    if data_format in {'yml', 'yaml'}:
        data = yaml.dump(spec)
    elif data_format == 'json':
        data = json.dumps(spec)
    else:
        raise Exception("Bad Format")

    if file_name:
        with open(file_name, 'w') as dst:
            dst.write(data)
    else:
        return data
