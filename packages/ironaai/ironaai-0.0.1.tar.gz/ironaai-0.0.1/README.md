

### API vs SDK
* Client side LLM invocation.
  - Our API endpoint of model-router, only recommends the model to use.
  - The sdk invokes the "recommended model" for the given prompt, gets the response back.

SDK also provides the following features which API endpoint doesn't via a common interface.
##### Features:
- Model routing functionality using the IronaAI API endpoints
- [] Support for async & sync requests of LLM-invocation.
- [] function calling,
- [] Tool binding using LiteLLM's function calling capabilities
- [] Error handling and retries
- [] Support for streaming, 
- [] and JSON mode (i.e. structured output)
- [] Detailed latency tracking and reporting - TBD
- [] Creation of preference IDs - TBD


* Retry logic (invocation or model-router)
* Unified Interface
* Tool binding



Export keys for provider you will use:

```
IRONAAI_API_KEY = "OUR_IRONAI_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
```

To use this client, you would initialize it like this:

```
client = IronaAI(
    models=["openai/gpt-3.5-turbo", "openai/gpt-4", "anthropic/claude-2"],
)
```

You can then use it for completions, function calling, and tool binding:


```
# Regular completion
response = client.completion(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    models=["openai/gpt-3.5-turbo", "openai/gpt-4", "anthropic/claude-2"],)

# Function calling
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
]
response = client.function_call(
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
    functions=functions
)

# Tool binding
def get_current_weather(location: str, unit: str = "fahrenheit"):
    """Get the current weather in a given location"""
    # Implementation here
    pass

tool_bound_client = client.bind_tools([get_current_weather])
response = tool_bound_client(messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}])
```


### Install Instructions

```
poetry install .
```

### Push this to PyPi

```
poetry build
poetry publish
```


Then users can simply install the package using pip:

```
pip install ironaai
```

