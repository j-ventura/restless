from enum import Enum
from functools import wraps
from typing import Callable
from inspect import signature


class Restrict:
    def __init__(self, check_function: Callable):
        self.check_function = check_function

        sig = signature(check_function)

        self.params = sig.parameters.keys()

    def __call__(self, func: Callable):
        sig = signature(func)

        assert all([p in sig.parameters for p in self.params])

        @wraps(func)
        def restricted(*args, **kwargs):
            self.check_function(**{p: kwargs[p] for p in self.params})

            return func(*args, **kwargs)

        return restricted


class Security(dict):
    pass


class BasicAuth(Security):
    name = 'Basic'

    def __init__(self):
        super().__init__(
            type='http',
            scheme='basic'
        )


class ApiKeyAuth(Security):
    class In(Enum):
        header = "header"
        query = "query"
        cookie = "cookie"

    def __init__(self, in_: In, name):
        self.name = name
        super().__init__(
            type='apiKey',
            name=name
        )

        self["in"] = in_.value
