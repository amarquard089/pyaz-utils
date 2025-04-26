from pydantic import BaseModel


class _Validator:

    @staticmethod
    def _is_serializeable_type(obj: type):
        if issubclass(obj, str):
            return True
        if issubclass(obj, int):
            return True
        if issubclass(obj, list):
            return _Validator._is_serializeable_type(obj.__args__[0])
        if issubclass(obj, bool):
            return True
        if issubclass(obj, dict):
            key, val = obj.__args__
            return _Validator._is_serializeable_type(
                key
            ) and _Validator._is_serializeable_type(val)
        if issubclass(obj, BaseModel):
            return True
        return False
