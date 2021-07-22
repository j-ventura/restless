import re
from collections import defaultdict
from typing import Callable, ClassVar, Iterable, List
from inspect import signature
from restless.interfaces import BaseRequest
from restless.util import FormData
from restless.parameters import BinaryParameter, BodyParameter
from restless.errors import Forbidden, Unauthorized, Missing
from pydantic.error_wrappers import ValidationError
from restless.security import Security
from pydantic import BaseModel


class PathHandler:
    def __init__(self, path, path_regex, method, http_method, tags=None, security=list):
        self.path = path.replace('<', '{').replace('>', '}')
        self.path_regex = path_regex
        self.method = method
        self.http_method = http_method
        self.tags = tags or []
        self.security = security

        self.sig = signature(method)
        self.parameters = {k: v.annotation or type(v.default) for k, v in self.sig.parameters.items()}

    def process_request(self, req: BaseRequest):
        params = {}
        method_params = {}
        match = self.path_regex.search(req.path)

        if match:
            params.update(match.groupdict().items())

        if req.headers:
            params.update(req.headers)

        if req.query:
            params.update(req.query)

        if isinstance(req.body, bytes):
            try:
                params.update(
                    FormData(req.body)
                )
            except AttributeError:
                params["body"] = req.body

        for param, value in params.items():
            if param not in self.parameters:
                continue
            else:
                method_params[param] = value if isinstance(value, FormData.File) else self.parameters[param](
                    value)

        for param, type_ in self.parameters.items():
            if type_ == BinaryParameter:
                method_params[param] = params.get('body')
            elif issubclass(type_, BodyParameter):
                method_params[param] = type_(**req.body)

        result = self.method(**method_params)

        if isinstance(result, tuple):
            if len(result) == 2:
                body, status, headers = result[0], result[1], {}
            else:
                body, status, headers = result
        else:
            body, status, headers = result, 200, {}

        expected_type = self.sig.return_annotation[status]

        if isinstance(body, Iterable) and not isinstance(body, (dict, str, BaseModel)):
            body = list(body)

            assert all(
                isinstance(rec, expected_type[0]) for rec in body
            ), f"All records should be of type '{expected_type.__name__e}'"
        else:
            assert isinstance(body, expected_type), f"The body should be of type '{expected_type.__name__}'"

        return body, status, headers


class Handler:
    REGEX = re.compile(r'(<[^/]+?>)')

    def __init__(self, request: ClassVar, response: ClassVar, use_camel_case=False):
        self.handlers = defaultdict(dict)
        self.Request = request
        self.Response = response
        self.use_camel_case = use_camel_case

    def handle(self, method: str, path: str, tags=None, security=[]) -> Callable:
        tokens = path.split('/')[1:]
        path_expressions = []
        target = self.handlers[len(tokens)]

        for token in tokens:
            if self.REGEX.match(token):
                path_expressions.append(
                    self.REGEX.sub('(?P\\1[^/]+)', token)
                )
                token = ''
            else:
                path_expressions.append(token)

            if token not in target:
                target[token] = {}

            target = target[token]

        def wrapped(f: Callable):
            path_regex = re.compile('/'.join(path_expressions) + '$')
            assert method.upper() not in target, f"'{path}' already has the '{method}' method"
            target[method.upper()] = PathHandler(
                path=path,
                path_regex=path_regex,
                method=f,
                http_method=method,
                tags=tags,
                security=security
            )
            return f

        return wrapped

    def select_handler(self, req: BaseRequest):
        tokens = req.path.split('/')[1:]
        target = self.handlers[len(tokens)]

        for token in tokens:
            if '' in target:
                target = target['']

            elif token in target:
                target = target[token]

        try:
            return target[req.method.upper()]
        except KeyError:
            raise Missing(f"Missing '{req.method}' on '{req.path}'")

    def __call__(self, event):
        req = self.Request(event, use_camel_case=self.use_camel_case)

        try:
            path_handler = self.select_handler(req)

            body, status, headers = path_handler.process_request(req)

            return self.Response(
                body=body,
                status_code=status,
                headers=headers,
                use_camel_case=self.use_camel_case
            )

        except (TypeError, AssertionError) as e:
            if e.args and 'missing' in e.args[0]:
                return self.Response(
                    {"error": str(e)},
                    400,
                    use_camel_case=self.use_camel_case
                )
            raise e

        except ValidationError as e:
            return self.Response(
                {"error": "Validation Error", "details": e.errors()},
                400,
                use_camel_case=self.use_camel_case
            )

        except Unauthorized as e:
            return self.Response(
                {"error": e.args[0]},
                401,
                use_camel_case=self.use_camel_case
            )

        except Forbidden as e:
            return self.Response(
                {"error": e.args[0]},
                403,
                use_camel_case=self.use_camel_case
            )

        except Missing as e:
            return self.Response(
                {"error": e.args[0]},
                404,
                use_camel_case=self.use_camel_case
            )
