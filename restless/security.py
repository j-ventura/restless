from enum import Enum


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
