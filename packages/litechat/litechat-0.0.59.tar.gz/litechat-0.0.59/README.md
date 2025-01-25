# LiteChat 🚀

LiteChat is a lightweight, OpenAI-compatible interface for running local LLM inference servers. It provides seamless integration with various open-source models while maintaining OpenAI-style API compatibility.

## Features ✨

- 🔄 OpenAI API compatibility
- 🌐 Web search integration
- 💬 Conversation memory
- 🔄 Streaming responses
- 🛠️ Easy integration with HuggingFace models
- 📦 Compatible with both litellm and OpenAI clients
- 🎯 Type-safe model selection

## Installation 🛠️

```bash
pip install litechat playwright
playwright install
```

## Available Models 🤖

LiteChat supports the following models:

- `Qwen/Qwen2.5-Coder-32B-Instruct`: Specialized coding model
- `Qwen/Qwen2.5-72B-Instruct`: Large general-purpose model
- `meta-llama/Llama-3.3-70B-Instruct`: Latest Llama 3 model
- `CohereForAI/c4ai-command-r-plus-08-2024`: Cohere's command model
- `Qwen/QwQ-32B-Preview`: Preview version of QwQ
- `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`: NVIDIA's Nemotron model
- `meta-llama/Llama-3.2-11B-Vision-Instruct`: Vision-capable Llama model
- `NousResearch/Hermes-3-Llama-3.1-8B`: Lightweight Hermes model
- `mistralai/Mistral-Nemo-Instruct-2407`: Mistral's instruction model
- `microsoft/Phi-3.5-mini-instruct`: Microsoft's compact Phi model

## Model Selection Helpers 🎯

LiteChat provides helper functions for type-safe model selection:

```python
from litechat import litechat_model, litellm_model

# For use with LiteChat native client
model = litechat_model("Qwen/Qwen2.5-72B-Instruct")

# For use with LiteLLM
model = litellm_model("Qwen/Qwen2.5-72B-Instruct")  # Returns "openai/Qwen/Qwen2.5-72B-Instruct"
```

## Quick Start 🚀

### Starting the Server

You can start the LiteChat server in two ways:

1. Using the CLI:
```bash
litechat_server
```

2. Programmatically:

```python
from litechat import litechat_server

if __name__ == "__main__":
    litechat_server(host="0.0.0.0", port=11437)
```

### Using with OpenAI Client

```python
import os
from openai import OpenAI

os.environ['OPENAI_BASE_URL'] = "http://localhost:11437/v1"
os.environ['OPENAI_API_KEY'] = "key123" # required, but not used

client = OpenAI()
response = client.chat.completions.create(
    model=litechat_model("NousResearch/Hermes-3-Llama-3.1-8B"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(response.choices[0].message.content)
```

### Using with LiteLLM

```python
import os

from litellm import completion
from litechat import OPENAI_COMPATIBLE_BASE_URL, litellm_model

os.environ["OPENAI_API_KEY"] = "key123"

response = completion(
    model=litellm_model("NousResearch/Hermes-3-Llama-3.1-8B"),
    messages=[{"content": "Hello, how are you?", "role": "user"}],
    api_base=OPENAI_COMPATIBLE_BASE_URL
)
print(response)
```

### Using LiteChat's Native Client

```python
from litechat import completion, genai, pp_completion
from litechat import litechat_model

# Basic completion
response = completion(
    prompt="What is quantum computing?",
    model="nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    web_search=True  # Enable web search
)

# Stream with pretty printing
pp_completion(
    prompt="Explain the theory of relativity",
    model="Qwen/Qwen2.5-72B-Instruct",
    conversation_id="physics_chat"  # Enable conversation memory
)

# Get direct response
result = genai(
    prompt="Write a poem about spring",
    model="meta-llama/Llama-3.3-70B-Instruct",
    system_prompt="You are a creative poet"
)
```

## Advanced Features 🔧

### Web Search Integration

Enable web search to get up-to-date information:

```python
response = completion(
    prompt="What are the latest developments in AI?",
    web_search=True
)
```

### Conversation Memory

Maintain context across multiple interactions:

```python
response = completion(
    prompt="Tell me more about that",
    conversation_id="unique_conversation_id"
)
```

### Streaming Responses

Get token-by-token streaming:

```python
for chunk in completion(
    prompt="Write a long story",
    stream=True
):
    print(chunk.choices[0].delta.content, end="", flush=True)
```

## API Reference 📚

### LiteAI Client

```python
from litechat import LiteAI, litechat_model

client = LiteAI(
    api_key="optional-key",  # Optional API key
    base_url="http://localhost:11437",  # Server URL
    system_prompt="You are a helpful assistant",  # Default system prompt
    web_search=False,  # Enable/disable web search by default
    model=litechat_model("nvidia/Llama-3.1-Nemotron-70B-Instruct-HF")  # Default model
)
```

### Completion Function Parameters

- `messages`: List of conversation messages or direct prompt string
- `model`: HuggingFace model identifier (use `litechat_model()` for type safety)
- `system_prompt`: System instruction for the model
- `temperature`: Control randomness (0.0 to 1.0)
- `stream`: Enable streaming responses
- `web_search`: Enable web search
- `conversation_id`: Enable conversation memory
- `max_tokens`: Maximum tokens in response
- `tools`: List of available tools/functions

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

For support, please open an issue on the GitHub repository or reach out to the maintainers.