import sys
from typing import Generic, Type, TypeVar

from azure.functions.decorators.function_app import FunctionBuilder
from pydantic import BaseModel

from pyaz_utils.durable._Validator import _Validator

_dependency_exc = None
try:
    import azure.durable_functions as df
    from azure.durable_functions.models.Task import TaskBase
except ImportError:
    _dependency_exc = sys.exc_info()
    raise Exception("please install using uv add pyaz-utils[durable]")


def to_json(self: BaseModel):
    return self.model_dump_json()


@classmethod
def from_json(cls: Type[BaseModel], val: str):
    return cls.model_validate_json(val)


_In = TypeVar("_In")
_Out = TypeVar("_Out")


class BaseInterface(Generic[_In, _Out]):

    def __init__(self, func: FunctionBuilder, inpt: Type[_In], outpt: Type[_Out]):
        self.func = func
        self.inpt = inpt
        self.outpt = outpt
        self._validate(inpt, outpt)

    def _validate(self, inpt: Type[_In], outpt: Type[_Out]):
        if _Validator._is_serializeable_type(
            inpt
        ) and _Validator._is_serializeable_type(outpt):
            return
        if not _Validator._is_serializeable_type(inpt):
            try:
                getattr(inpt, "to_json")
            except AttributeError as e:
                raise ValueError(
                    'The provided inpt type has no "to_json" method'
                ) from e
        if not _Validator._is_serializeable_type(outpt):
            try:
                getattr(outpt, "from_json")
            except AttributeError as e:
                raise ValueError(
                    'The provided output type has not "from_json" method'
                ) from e

    def _monkey_patch(self):
        if issubclass(self.inpt, BaseModel):
            setattr(self.inpt, to_json.__name__, to_json)
        if hasattr(self.inpt, "__origin__"):
            if issubclass(self.inpt.__origin__, list):  # type: ignore
                if issubclass(self.inpt.__args__[0], BaseModel):  # type: ignore
                    setattr(self.inpt, to_json.__name__, to_json)

        if issubclass(self.outpt, BaseModel):
            setattr(self.outpt, from_json.__name__, from_json)
        if hasattr(self.outpt, "__origin__"):
            if issubclass(self.outpt.__origin__, list):  # type: ignore
                if issubclass(self.outpt.__args__[0], BaseModel):  # type: ignore
                    setattr(self.outpt, from_json.__name__, from_json)
