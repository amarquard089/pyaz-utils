
# Durable Functions

Typical Usage <br>
**No type inference, functions are called via strings.**
```python
# see https://learn.microsoft.com/en-us/azure/azure-functions/durable/quickstart-python-vscode?tabs=windows%2Cazure-cli-set-indexing-flag&pivots=python-mode-decorators
import azure.durable_functions as df

app = df.DFApp()

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response

# Orchestrator
@app.orchestration_trigger(context_name="context")
def hello_orchestrator(context):
    result1 = yield context.call_activity("hello", "Seattle")
    result2 = yield context.call_activity("hello", "Tokyo")
    result3 = yield context.call_activity("hello", "London")

    return [result1, result2, result3]

# Activity
@app.activity_trigger(input_name="city")
def hello(city: str):
    return f"Hello {city}"

```


**Using pyaz_utils**

```python
from pyaz_utils.durable import make_activity_interface, make_orchestrator_interface

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = hello_orchestrator.start(client=client)
    response = client.create_check_status_response(req, instance_id)
    return response

# Orchestrator
@make_orchestrator_interface(inpt=None, outpt=list[str])
@app.orchestration_trigger(context_name="context")
def hello_orchestrator(context):
    result1 = yield from hello.call(context=context, inpt="Seattle")
    result2 = yield from hello.call(context=context, inpt="Tokyo")
    result3 = yield from hello.call(context=context, inpt="London")

    return [result1, result2, result3]


# Activity
@make_activity_interface(inpt=str, outpt=str)
@app.activity_trigger(input_name="city")
def hello(city: str):
    return f"Hello {city}"
```

