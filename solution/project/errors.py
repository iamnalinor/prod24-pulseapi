class ClientRequestError(Exception):
    def __init__(self, status_code: int, reason: str):
        self.status_code = status_code
        self.reason = reason


def assert400(condition, reason: str = "invalid data passed"):
    if not condition:
        raise ClientRequestError(400, reason)


def assert404(condition, reason: str = "object not found"):
    if not condition:
        raise ClientRequestError(404, reason)


def assert409(condition, reason: str = "conflict"):
    if not condition:
        raise ClientRequestError(409, reason)
