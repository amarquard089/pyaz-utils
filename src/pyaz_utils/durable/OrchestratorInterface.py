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


class OrchestratorInterface(BaseInterface[_In, _Out]):
    @overload
    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        instance_id: str | None = None,
        *,
        retry_option: df.RetryOptions,
    ) -> Generator[TaskBase, Any, _Out]: ...

    @overload
    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        instance_id: str | None = None,
        *,
        retry_option: None,
    ) -> Generator[TaskBase, Any, _Out]: ...

    @overload
    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        instance_id: str | None = None,
    ) -> Generator[TaskBase, Any, _Out]: ...

    def call(
        self,
        context: df.DurableOrchestrationContext,
        inpt: _In,
        instance_id: str | None = None,
        *,
        retry_option: df.RetryOptions | None = None,
    ) -> Generator[TaskBase, Any, _Out]:
        if retry_option:
            result = yield context.call_sub_orchestrator_with_retry(
                name=self.func._function._name,
                retry_options=retry_option,
                input_=inpt,
                instance_id=instance_id,
            )
        else:
            result = yield context.call_sub_orchestrator(
                name=self.func._function._name,
                input_=inpt,
                instance_id=instance_id,
            )
        if self.outpt is None:
            return
        return cast(_Out, result)

    async def start(
        self,
        client: df.DurableOrchestrationClient,
        inpt: _In,
        instance_id: str | None = None,
    ):
        instance_id = await client.start_new(
            orchestration_function_name=self.func._function._name,
            client_input=inpt,
            instance_id=instance_id,
        )
        return instance_id


@overload
def make_orchestrator_interface(
    inpt: Type[_In], outpt: Type[_Out]
) -> Callable[..., OrchestratorInterface[_In, _Out]]: ...


@overload
def make_orchestrator_interface(
    inpt: Type[_In], outpt: NoneType
) -> Callable[..., OrchestratorInterface[_In, NoneType]]: ...


def make_orchestrator_interface(
    inpt: Type[_In], outpt: Type[_Out] | NoneType
) -> (
    Callable[..., OrchestratorInterface[_In, _Out]]
    | Callable[..., OrchestratorInterface[_In, NoneType]]
):
    def _make_interface(func: FunctionBuilder) -> OrchestratorInterface[_In, _Out]:
        return OrchestratorInterface[_In, _Out](func, inpt, outpt)

    def _make_nullable_interface(
        func: FunctionBuilder,
    ) -> OrchestratorInterface[_In, NoneType]:
        return OrchestratorInterface[_In, NoneType](func, inpt, outpt)

    if outpt is None:
        return _make_nullable_interface
    return _make_interface
