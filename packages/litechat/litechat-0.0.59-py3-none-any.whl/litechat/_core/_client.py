from __future__ import annotations

import json
from typing import List, Optional, Union, Iterator, Dict
from typing_extensions import Literal
import requests
from pydantic import BaseModel

from litechat.types.hf_models import HFChatModels


# Models matching OpenAI spec exactly
class ChoiceDeltaFunctionCall(BaseModel):
    arguments: Optional[str] = None
    name: Optional[str] = None


class ChoiceDeltaToolCallFunction(BaseModel):
    arguments: Optional[str] = None
    name: Optional[str] = None


class ChoiceDeltaToolCall(BaseModel):
    index: int
    id: Optional[str] = None
    function: Optional[ChoiceDeltaToolCallFunction] = None
    type: Optional[Literal["function"]] = None


class ChoiceDelta(BaseModel):
    content: Optional[str] = None
    function_call: Optional[ChoiceDeltaFunctionCall] = None
    refusal: Optional[str] = None
    role: Optional[Literal["system", "user", "assistant", "tool"]] = None
    tool_calls: Optional[List[ChoiceDeltaToolCall]] = None


class Choice(BaseModel):
    delta: ChoiceDelta
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter", "function_call"]] = None
    index: int
    logprobs: Optional[dict] = None


class CompletionUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ChatCompletionChunk(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: Literal["chat.completion.chunk"]
    service_tier: Optional[Literal["scale", "default"]] = None
    system_fingerprint: Optional[str] = None
    usage: Optional[CompletionUsage] = None


class ChatCompletionMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatChoice(BaseModel):
    message: Optional[ChatCompletionMessage] = None


class ChatCompletion(BaseModel):
    id: str
    choices: List[ChatChoice]
    created: int
    model: str
    object: str
    usage: Optional[CompletionUsage] = None
    system_fingerprint: Optional[str] = None


class Completions:
    def __init__(self, client: OpenAI):
        self._client = client

    def create(
        self,
        messages: List[Dict[str, str]],
        model: Optional[HFChatModels] =None,
        temperature: float = 1.0,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        url = f"{self._client.base_url}/v1/chat/completions"

        payload = {
            "messages": messages,
            "model": model or self._client.model,
            "temperature": temperature,
            "stream": stream,
            "web_search": kwargs.pop("web_search", False),
            "conv_id": kwargs.pop("conversation_id", ""),
            **kwargs
        }

        if stream:
            response = requests.post(url, json=payload, stream=True)
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code},"
                                f"Exceptions: {response.content}")

            def generate_chunks():
                for line in response.iter_lines():
                    if line:
                        try:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                json_str = line_str[6:]  # Remove 'data: ' prefix
                                if json_str == '[DONE]':
                                    break
                                chunk = json.loads(json_str)
                                yield ChatCompletionChunk(**chunk)
                        except json.JSONDecodeError:
                            continue

            return generate_chunks()
        else:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code},"
                                f"Exceptions: {response.content}")
            return ChatCompletion(**response.json())


class Chat:
    def __init__(self, client: OpenAI):
        self.completions = Completions(client)


class LiteAI:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11437",
        system_prompt: Optional[str] = None,
        web_search: Optional[bool] = None,
        model:Optional[HFChatModels] = None
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.system_prompt = system_prompt
        self.web_search = web_search
        self.model = model
        self.chat = Chat(self)
        self._set_features_in_chat()

    def _set_features_in_chat(self):
        pass


OpenAI = LiteAI


def main():
    client = LiteAI()

    print("Streaming response:")
    for chunk in client.chat.completions.create(
        messages=[{"role": "user", "content": "when is kohli born?"}],
        stream=True,
        conversation_id='1234',
        web_search=True
    ):
        print(chunk.model_dump())

    # print("\nNon-streaming response:")
    # Create a chat completion request with a user message asking for the sum of 2 and 2
    # response = client.chat.completions.create(
    #     messages=[{"role": "user", "content": "What is 2+2?"}],
    #     stream=False
    # )
    # Print the model dump of the response
    # print(response.model_dump())


if __name__ == "__main__":
    main()
