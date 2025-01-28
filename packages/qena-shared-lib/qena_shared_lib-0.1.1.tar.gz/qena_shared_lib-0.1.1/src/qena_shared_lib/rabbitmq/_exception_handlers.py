from typing import Annotated

from pydantic import ValidationError

from ..dependencies.miscellaneous import DependsOn
from ..exceptions import ServiceException, Severity
from ..logging import LoggerProvider
from ..logstash._base import BaseLogstashSender
from ._exceptions import RabbitMQException
from ._listener import ListenerContext

__all__ = [
    "handle_general_mq_exception",
    "handle_microservice_exception",
    "handle_rabbitmq_exception",
    "handle_validation_error",
]

RABBITMQ_EXCEPTION_HANDLER_LOGGER_NAME = "rabbitmq.exception_handler"


def handle_rabbitmq_exception(
    context: ListenerContext,
    exception: RabbitMQException,
    logstash: Annotated[BaseLogstashSender, DependsOn(BaseLogstashSender)],
    logger_provider: Annotated[LoggerProvider, DependsOn(LoggerProvider)],
):
    logger = logger_provider.get_logger(RABBITMQ_EXCEPTION_HANDLER_LOGGER_NAME)

    if not exception.logstash_logging:
        logger.warning("%r", exception)

        return

    logstash.warning(
        message=exception.message,
        tags=exception.tags
        or [
            "RabbitMQ",
            "RabbitMQException",
            str(exception.code),
            context.queue,
            context.listener_name or "__default__",
        ],
        extra=exception.extra
        or {
            "serviceType": "RabbitMQ",
            "queue": context.queue,
            "listenerName": context.listener_name,
            "exception": "RabbitMQException",
        },
    )


def handle_validation_error(
    context: ListenerContext,
    exception: ValidationError,
    logstash: Annotated[BaseLogstashSender, DependsOn(BaseLogstashSender)],
):
    logstash.error(
        message=f"invalid rabbitmq request data at queue `{context.queue}` and listener `{context.listener_name}`",
        tags=[
            "RabbitMQ",
            "ValidationError",
            context.queue,
            context.listener_name or "__default__",
        ],
        extra={
            "serviceType": "RabbitMQ",
            "queue": context.queue,
            "listenerName": context.listener_name,
            "exception": "ValidationError",
        },
        exception=exception,
    )


def handle_microservice_exception(
    context: ListenerContext,
    exception: ServiceException,
    logstash: Annotated[BaseLogstashSender, DependsOn(BaseLogstashSender)],
    logger_provider: Annotated[LoggerProvider, DependsOn(LoggerProvider)],
):
    logger = logger_provider.get_logger(RABBITMQ_EXCEPTION_HANDLER_LOGGER_NAME)
    tags = [
        "RabbitMQ",
        type(exception).__name__,
        context.queue,
        context.listener_name or "__default__",
    ]

    if exception.tags:
        exception.tags.extend(tags)

    extra = {
        "serviceType": "RabbitMQ",
        "queue": context.queue,
        "listenerName": context.listener_name,
        "exception": exception.__class__.__name__,
    }

    if exception.extra:
        exception.extra.update(extra)

    exc_info = (
        (type(exception), exception, exception.__traceback__)
        if exception.extract_exc_info
        else None
    )

    match exception.severity:
        case Severity.HIGH:
            logstash_logger_method = logstash.error
            logger_method = logger.error
        case Severity.MEDIUM:
            logstash_logger_method = logstash.warning
            logger_method = logger.warning
        case _:
            logstash_logger_method = logstash.info
            logger_method = logger.info

    if exception.logstash_logging:
        logstash_logger_method(
            message=exception.message,
            tags=exception.tags or tags,
            extra=exception.extra or extra,
            exception=exception if exception.extract_exc_info else None,
        )
    else:
        logger_method(
            "\nRabbitMQ `%s` -> `%s`\n%s",
            context.queue,
            context.listener_name,
            exception.message,
            exc_info=exc_info,
        )


def handle_general_mq_exception(
    context: ListenerContext,
    exception: Exception,
    logstash: Annotated[BaseLogstashSender, DependsOn(BaseLogstashSender)],
):
    logstash.error(
        message=f"something went wrong while consuming message on queue `{context.queue}` and listener `{context.listener_name}`",
        tags=[
            "RabbitMQ",
            exception.__class__.__name__,
            context.queue,
            context.listener_name or "__default__",
        ],
        extra={
            "serviceType": "RabbitMQ",
            "queue": context.queue,
            "listenerName": context.listener_name,
            "exception": exception.__class__.__name__,
        },
        exception=exception,
    )
