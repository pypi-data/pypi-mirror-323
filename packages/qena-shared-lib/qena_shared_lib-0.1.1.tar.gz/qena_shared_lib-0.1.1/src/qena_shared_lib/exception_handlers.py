from typing import Any

from fastapi import Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .dependencies.http import get_service
from .exceptions import ServiceException, Severity
from .logging import LoggerProvider
from .logstash._base import BaseLogstashSender

__all__ = [
    "handle_service_exception",
    "handle_request_validation_error",
    "handle_general_http_exception",
]


def handle_service_exception(
    request: Request, exception: ServiceException
) -> Response:
    logstash = get_service(app=request.app, service_key=BaseLogstashSender)
    logger_provider = get_service(app=request.app, service_key=LoggerProvider)
    logger = logger_provider.get_logger("http.exception_handler")
    exception_severity = exception.severity or Severity.LOW
    message = exception.message
    tags = [
        "HTTP",
        request.method,
        request.url.path,
        exception.__class__.__name__,
    ]

    if exception.tags:
        exception.tags.extend(tags)

    extra = {
        "serviceType": "HTTP",
        "method": request.method,
        "path": request.url.path,
        "exception": exception.__class__.__name__,
    }

    if exception.extra:
        exception.extra.update(extra)

    exc_info = (
        (type(exception), exception, exception.__traceback__)
        if exception.extract_exc_info
        else None
    )

    match exception_severity:
        case Severity.LOW:
            logstash_logger_method = logstash.info
            logger_method = logger.info
        case Severity.MEDIUM:
            logstash_logger_method = logstash.warning
            logger_method = logger.warning
        case _:
            message = "something went wrong"
            logstash_logger_method = logstash.error
            logger_method = logger.error

    if exception.logstash_logging:
        logstash_logger_method(
            message=exception.message,
            tags=exception.tags or tags,
            extra=exception.extra or extra,
            exception=exception if exception.extract_exc_info else None,
        )
    else:
        logger_method(
            "\n%s %s\n%s",
            request.method,
            request.url.path,
            exception.message,
            exc_info=exc_info,
        )

    content: dict[str, Any] = {
        "severity": exception_severity.name
        if exception_severity
        else Severity.LOW.name,
        "message": message,
    }

    if exception.response_code is not None:
        content["code"] = exception.response_code

    if exception.corrective_action is not None:
        content["correctiveAction"] = exception.corrective_action

    if exception.body is not None:
        content.update(dict(exception.body))

    return JSONResponse(
        content=content,
        status_code=exception.status_code
        or _status_code_from_severity(exception.severity),
        headers=exception.headers,
    )


def handle_request_validation_error(
    request: Request, error: RequestValidationError
) -> Response:
    logger_provider = get_service(app=request.app, service_key=LoggerProvider)
    logger = logger_provider.get_logger("http.exception_handler")
    message = "invalid request data"

    logger.warning("\n%s %s\n%s", request.method, request.url.path, message)

    return JSONResponse(
        content={
            "severity": Severity.MEDIUM.name,
            "message": message,
            "code": 100,
            "detail": jsonable_encoder(error.errors()),
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def handle_general_http_exception(
    request: Request, exception: Exception
) -> Response:
    logstash = get_service(app=request.app, service_key=BaseLogstashSender)

    logstash.error(
        message=f"something went wrong on endpoint `{request.method} {request.url.path}`",
        tags=[
            "HTTP",
            request.method,
            request.url.path,
            exception.__class__.__name__,
        ],
        extra={
            "serviceType": "HTTP",
            "method": request.method,
            "path": request.url.path,
            "exception": exception.__class__.__name__,
        },
        exception=exception,
    )

    return JSONResponse(
        content={
            "severity": Severity.HIGH.name,
            "message": "something went wrong",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _status_code_from_severity(severity: Severity | None) -> int:
    if (
        severity is None
        or severity == Severity.LOW
        or severity == Severity.MEDIUM
    ):
        return status.HTTP_400_BAD_REQUEST

    return status.HTTP_500_INTERNAL_SERVER_ERROR
