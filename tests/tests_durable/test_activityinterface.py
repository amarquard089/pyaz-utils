from dataclasses import dataclass

import azure.durable_functions as df
import pytest
from azure.functions.decorators.function_app import FunctionBuilder
from pydantic import BaseModel

from pyaz_utils.durable import ActivityInterface


@dataclass
class DataclassTest:
    name: str
    age: int


class BaseModelTest(BaseModel):
    name: str
    age: int


@pytest.fixture
def app():
    df_app = df.DFApp()
    yield df_app


@pytest.fixture
def str_activity_str(app: df.DFApp):
    @app.activity_trigger(input_name="inpt")
    def say_hello(inpt: str):
        return f"Hello {inpt}"

    yield say_hello


@pytest.fixture
def BaseModel_activity_str(app: df.DFApp):

    @app.activity_trigger(input_name="inpt")
    def say_hello(inpt: BaseModelTest) -> str:
        return f"Hello {inpt}"

    yield say_hello


@pytest.fixture
def dataclass_activity_str(app: df.DFApp):

    @app.activity_trigger(input_name="inpt")
    def say_hello(inpt: DataclassTest) -> str:
        return f"Hello {inpt}"

    yield say_hello


def test_init(str_activity_str: FunctionBuilder):
    act_int = ActivityInterface(func=str_activity_str, inpt=str, outpt=str)
    assert issubclass(act_int.inpt, str)
    assert issubclass(act_int.outpt, str)


def test_init_raise(dataclass_activity_str: FunctionBuilder):
    with pytest.raises(ValueError):
        ActivityInterface(func=dataclass_activity_str, inpt=DataclassTest, outpt=str)


def test_init_basemodel(BaseModel_activity_str: FunctionBuilder):
    act_int = ActivityInterface(
        func=BaseModel_activity_str, inpt=BaseModelTest, outpt=str
    )
    assert issubclass(act_int.inpt, BaseModelTest)
    assert issubclass(act_int.outpt, str)


# def test_make_activity(app: df.DFApp):
#     @make_activity_interface(inpt=str,outpt=str)
#     @app.activity_trigger(input_name="city")
#     def hello(city: str) -> str:
#         return f"hello {city}"

#     hello.call(context=)
