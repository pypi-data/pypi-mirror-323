class RabbitMQException(Exception):
    def __init__(
        self,
        code: int,
        message: str,
        tags: list[str] | None = None,
        extra: dict[str, str] | None = None,
        logstash_logging: bool = True,
        extract_exc_info: bool = True,
    ):
        self._code = code
        self._message = message
        self._tags = tags
        self._extra = extra
        self._logstash_logging = logstash_logging
        self._extract_exc_info = extract_exc_info

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def tags(self) -> list[str] | None:
        return self._tags

    @property
    def extra(self) -> dict[str, str] | None:
        return self._extra

    @property
    def logstash_logging(self) -> bool:
        return self._logstash_logging

    @property
    def extract_exc_info(self) -> bool:
        return self._extract_exc_info

    def __str__(self) -> str:
        return f"message `{self.message}`, code `{self.code}`"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ( message: `{self._message}`, code: {self._code} )"
