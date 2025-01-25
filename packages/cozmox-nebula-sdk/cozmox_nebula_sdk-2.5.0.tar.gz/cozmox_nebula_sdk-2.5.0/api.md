# Nebula

Types:

```python
from cozmox_sdk.types import NebulaHelloResponse
```

Methods:

- <code title="get /v1/nebula/hello">client.nebula.<a href="./src/cozmox_sdk/resources/nebula.py">hello</a>() -> <a href="./src/cozmox_sdk/types/nebula_hello_response.py">NebulaHelloResponse</a></code>

# Outbound

Types:

```python
from cozmox_sdk.types import OutboundCreateCallResponse, OutboundRetrieveCallResponse
```

Methods:

- <code title="post /v1/outbound/create-call">client.outbound.<a href="./src/cozmox_sdk/resources/outbound.py">create_call</a>(\*\*<a href="src/cozmox_sdk/types/outbound_create_call_params.py">params</a>) -> <a href="./src/cozmox_sdk/types/outbound_create_call_response.py">OutboundCreateCallResponse</a></code>
- <code title="post /v1/outbound/retrieve-call">client.outbound.<a href="./src/cozmox_sdk/resources/outbound.py">retrieve_call</a>(\*\*<a href="src/cozmox_sdk/types/outbound_retrieve_call_params.py">params</a>) -> <a href="./src/cozmox_sdk/types/outbound_retrieve_call_response.py">OutboundRetrieveCallResponse</a></code>

# Concurrency

Types:

```python
from cozmox_sdk.types import ConcurrencyHelloResponse
```

Methods:

- <code title="get /v1/concurrency/retrieve">client.concurrency.<a href="./src/cozmox_sdk/resources/concurrency.py">hello</a>() -> <a href="./src/cozmox_sdk/types/concurrency_hello_response.py">ConcurrencyHelloResponse</a></code>
