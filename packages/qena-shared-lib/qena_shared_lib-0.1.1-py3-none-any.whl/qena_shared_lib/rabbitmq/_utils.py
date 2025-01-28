from pydantic import TypeAdapter

__all__ = ["TypeAdapterCache"]


class TypeAdapterCache:
    _cache = {}

    @classmethod
    def cache_annotation(cls, annotation: type):
        if annotation not in cls._cache:
            cls._cache[annotation] = TypeAdapter(annotation)

    @classmethod
    def get_type_adapter(cls, annotation: type) -> TypeAdapter:
        cls.cache_annotation(annotation)

        return cls._cache[annotation]
