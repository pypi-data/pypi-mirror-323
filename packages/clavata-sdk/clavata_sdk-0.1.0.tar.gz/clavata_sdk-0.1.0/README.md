# SDK

This is the Clavata SDK for Python.

## Usage

The SDK is quite simple to use. First it needs to be imported (assuming of course that you're using this as an external package):

```python
from clavata_sdk import ClavataClient
```

Next, you'll need a Clavata API key to instantiate the client:

```python
api_key = "YOUR_API_KEY"

# Now instantiate the client with your API key:
client = ClavataClient(host="gateway.app.clavata.ai", port=443, auth_token=api_key)
```

> If you prefer, the `auth_token` parameter can be omitted and the API key can be set via the environment. To do this simply set the `CLAVATA_API_KEY` environment variable.

Finally, you can call various methods on the client with the generated request and response models:

```python
# Async request
response = client.create_job(CreateJobRequest(name="my-job", ...))

# Streaming request
async for response in client.evaluate(EvaluateRequest(name="my-job", ...)):
    print(response)
```
