import sys
from types import NoneType
from typing import Any, Callable, Generator, Type, TypeVar, cast, overload

from azure.functions.decorators.function_app import FunctionBuilder

from .BaseInterface import BaseInterface

_dependency_exc = None
try:
    import azure.durable_functions as df
    from azure.durable_functions.models.Task import TaskBase
except ImportError:
    _dependency_exc = sys.exc_info()
    raise Exception("please install using uv add pyaz-utils[durable]")

_In = TypeVar("_In")
_Out = TypeVar("_Out")


class ActivityInterface(BaseInterface[_In, _Out]):
    @overload
    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        retry_option: df.RetryOptions,
    ) -> Generator[TaskBase, Any, _Out]: ...

    @overload
    def call(
        self, context: df.DurableOrchestrationContext, inpt: _In, retry_option: None
    ) -> Generator[TaskBase, Any, _Out]: ...

    @overload
    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
    ) -> Generator[TaskBase, Any, _Out]: ...

    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        retry_option: df.RetryOptions | None = None,
    ) -> Generator[TaskBase, Any, _Out]:
        if retry_option:
            result = yield context.call_activity_with_retry(
                name=self.func._function._name, input_=inpt, retry_options=retry_option
            )
        else:
            result = yield context.call_activity(
                name=self.func._function._name, input_=inpt
            )
        if self.outpt is None:
            return
        return cast(_Out, result)

    async def __call__(self, *args, **kwargs):
        return await self.func(*args, **kwargs)


@overload
def make_activity_interface(
    inpt: Type[_In], outpt: Type[_Out]
) -> Callable[..., ActivityInterface[_In, _Out]]: ...


@overload
def make_activity_interface(
    inpt: Type[_In], outpt: NoneType
) -> Callable[..., ActivityInterface[_In, NoneType]]: ...


def make_activity_interface(
    inpt: Type[_In], outpt: Type[_Out] | NoneType
) -> (
    Callable[..., ActivityInterface[_In, _Out]]
    | Callable[..., ActivityInterface[_In, NoneType]]
):
    def _make_interface(func: FunctionBuilder) -> ActivityInterface[_In, _Out]:
        return ActivityInterface[_In, _Out](func, inpt, outpt)

    def _make_nullable_interface(
        func: FunctionBuilder,
    ) -> ActivityInterface[_In, NoneType]:
        return ActivityInterface[_In, NoneType](func, inpt, outpt)

    if outpt is None:
        return _make_nullable_interface
    return _make_interface
