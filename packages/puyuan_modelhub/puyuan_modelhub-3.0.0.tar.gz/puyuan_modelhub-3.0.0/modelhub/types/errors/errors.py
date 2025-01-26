from ._base import ModelhubException
from .status_code import HTTP_CODE, MODELHUB_CODE


class AuthenticationError(ModelhubException):
    """AuthError: Exception for authentication error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.UNAUTHORIZED,
        app_code: int = MODELHUB_CODE.UNAUTHORIZED,
        msg: str = "Authentication Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class ModelNotFoundError(ModelhubException):
    """ModelNotFoundError: Exception for model not found"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.MODEL_NOT_FOUND,
        app_code: int = MODELHUB_CODE.MODEL_NOT_FOUND,
        msg: str = "Model Not Found",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class GroupNotFoundError(ModelhubException):
    """GroupNotFoundError: Exception for group not found"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.GROUP_NOT_FOUND,
        app_code: int = MODELHUB_CODE.GROUP_NOT_FOUND,
        msg: str = "Group Not Found",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class GroupExistsError(ModelhubException):
    """GroupExistsError: Exception for group already exists"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.GROUP_ALREADY_EXISTS,
        app_code: int = MODELHUB_CODE.GROUP_ALREADY_EXISTS,
        msg: str = "Group Already Exists",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class ModelLoadError(ModelhubException):
    """ModelLoadError: Exception for model load error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.INTERNAL_ERROR,
        app_code: int = MODELHUB_CODE.INTERNAL_ERROR,
        msg: str = "Model Load Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class IncorrectAPIKeyError(ModelhubException):
    """IncorrectAPIKeyError: Exception for incorrect API key error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.UNAUTHORIZED,
        app_code: int = MODELHUB_CODE.UNAUTHORIZED,
        msg: str = "Incorrect API Key",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class InternalServerError(ModelhubException):
    """InternalServerError: Exception for internal server error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.INTERNAL_ERROR,
        app_code: int = MODELHUB_CODE.INTERNAL_ERROR,
        msg: str = "Internal Server Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class RateLimitError(ModelhubException):
    """APIRateLimitError: Exception for API rate limit error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.API_RATE_LIMIT,
        app_code: int = MODELHUB_CODE.API_RATE_LIMIT,
        msg: str = "API Rate Limit Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class BillLimitError(ModelhubException):
    """BillLimitError: Exception for bill limit error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.BILL_LIMIT,
        app_code: int = MODELHUB_CODE.BILL_LIMIT,
        msg: str = "Bill Limit Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class BadParamsError(ModelhubException):
    """BadParamsError: Exception for bad parameters error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.BAD_PARAMS,
        app_code: int = MODELHUB_CODE.BAD_PARAMS,
        msg: str = "Bad Parameters Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class ModelGenerateError(ModelhubException):
    """LocalModelGenerateError: Exception for local model generation error"""

    def __init__(
        self,
        http_code: int = HTTP_CODE.INTERNAL_ERROR,
        app_code: int = MODELHUB_CODE.INTERNAL_ERROR,
        msg: str = "Model Generate Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class APITimeoutError(ModelhubException):
    def __init__(
        self,
        http_code: int = HTTP_CODE.API_TIMEOUT,
        app_code: int = MODELHUB_CODE.API_TIMEOUT,
        msg: str = "API Timeout",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class BadResponseError(ModelhubException):
    def __init__(
        self,
        http_code: int = HTTP_CODE.BAD_RESPONSE,
        app_code: int = MODELHUB_CODE.BAD_RESPONSE,
        msg: str = "Bad Response",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class APIConnectionError(ModelhubException):
    def __init__(
        self,
        http_code: int = HTTP_CODE.API_CONNECTION_ERROR,
        app_code: int = MODELHUB_CODE.API_CONNECTION_ERROR,
        msg: str = "API Connnection Error",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class ModelNotStartedError(ModelhubException):
    def __init__(
        self,
        http_code: int = HTTP_CODE.MODEL_NOT_STARTED,
        app_code: int = MODELHUB_CODE.MODEL_NOT_STARTED,
        msg: str = "Model Not Started",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)


class ManagerNotLoadedError(ModelhubException):
    def __init__(
        self,
        http_code: int = HTTP_CODE.MANAGER_NOT_LOADED,
        app_code: int = MODELHUB_CODE.MANAGER_NOT_LOADED,
        msg: str = "Manager Not Loaded",
        **kwargs,
    ):
        super().__init__(http_code, app_code=app_code, msg=msg, **kwargs)
