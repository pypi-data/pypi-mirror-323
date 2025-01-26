import json


class ModelhubException(Exception):
    def __init__(self, http_code: int = 200, app_code: int = 0, msg: str = "", **kwargs):
        self.code = http_code
        self.app_code = app_code
        self.msg = msg
        self.context = kwargs

    def __str__(self):
        return json.dumps({"code": self.app_code, "msg": self.msg, "context": self.context})

    __repr__ = __str__
