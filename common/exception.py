from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ErrorDetail
from common.response import StandardAPIResponse
from common.utils.logging import logger
from rest_framework.utils.serializer_helpers import ReturnDict


class StandardAPIException(APIException):
    """
    Exception class to throw standard API Exceptions with error_code and user-friendly
    error_message.
    """

    status_code = 400
    default_code = "error"
    default_detail = "Error Occurred"
    default_info = None

    def __init__(self, code, detail, status_code, info=None):
        super().__init__(detail=detail, code=code)
        self.code = code if code else self.default_code
        self.info = info
        self.status_code = status_code


class StandardExceptionHandler:
    """
    Exception Handler class to handle and report API exceptions as per
    HelixBeat API Style Guide.
    """

    @classmethod
    def handle(cls, exc, context):
        response = exception_handler(exc, context)
        if cls.is_path_whitelisted(context=context):
            try:
                if response is not None and isinstance(exc, StandardAPIException):
                    return cls._handle_standard_api_exception(exc, response)

                if response is not None and isinstance(exc, APIException):
                    return cls._handle_inbuilt_api_exception(exc, response)

            except Exception as e:
                logger.error(
                    f"Exception occurred while parsing API exception: {str(e)}"
                )

        return response

    @classmethod
    def is_path_whitelisted(cls, context):
        # path = context.get("request")._request.path
        return True

    @classmethod
    def _handle_standard_api_exception(cls, exc, response):
        error_code, error_message = None, None
        if hasattr(exc, "code"):
            error_code = getattr(exc, "code")
        if hasattr(exc, "detail"):
            error_message = exc.detail.__str__()
        errors_data = [{"code": error_code, "message": error_message}]
        return StandardAPIResponse(
            data=errors_data,
            status=response.status_code,
            headers=response.headers,
        )

    @classmethod
    def flatten_error_detail(cls, error_detail, parent_key=""):
        items = []
        for key, value in error_detail.items():
            new_key = parent_key + "." + key if parent_key else key
            if isinstance(value, dict):
                items.extend(cls.flatten_error_detail(value, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items)

    @classmethod
    def _handle_inbuilt_api_exception(cls, exc, response):
        errors_data = []
        if hasattr(exc, "detail"):
            error_detail = exc.detail

            if isinstance(error_detail, list):
                for error in error_detail:
                    errors_data.append(
                        {
                            "code": error.code,
                            "message": cls.normalize_message(error.__str__()),
                        }
                    )

            elif isinstance(error_detail, ErrorDetail):
                errors_data.append(
                    {
                        "code": error_detail.code,
                        "message": cls.normalize_message(error_detail.__str__()),
                    }
                )

            elif isinstance(error_detail, dict):
                error_detail = cls.flatten_error_detail(error_detail)
                code = error_detail.get("code")
                if isinstance(code, ErrorDetail):
                    errors_data.append(
                        {
                            "code": code.code,
                            "message": cls.normalize_message(code.__str__()),
                        }
                    )

                if code is None:
                    for k, v in error_detail.items():
                        if isinstance(v, list):
                            v_0 = v[0]
                            errors_data.append(
                                {
                                    "code": v_0.code,
                                    "message": cls.normalize_message(v_0.__str__()),
                                    "field": k,
                                }
                            )

            elif isinstance(error_detail, ReturnDict):
                detail = list(error_detail.values())[0]

                if isinstance(detail, list):
                    for error in detail:
                        errors_data.append(
                            {
                                "code": error.code,
                                "message": cls.normalize_message(error.__str__()),
                            }
                        )

                if isinstance(detail, ErrorDetail):
                    errors_data.append(
                        {
                            "code": detail.code,
                            "message": cls.normalize_message(detail.__str__()),
                        }
                    )

        return StandardAPIResponse(
            data=errors_data,
            status=response.status_code,
            headers=response.headers,
        )

    @classmethod
    def normalize_message(cls, message: str) -> str:
        if "user group with this name already exists" in message.lower():
            return "Role category with this name already exists."
        return message


def standard_api_exception_handler(exc, context):
    """
    Exception Handler function that invokes the HelixBeat standard API exception handler

    Args:
        exc:
        context:

    Returns:

    """
    return StandardExceptionHandler.handle(exc, context)
