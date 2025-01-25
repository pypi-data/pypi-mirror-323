import asyncio
import json
import time
import uuid
import uvicorn

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Union, Any, Dict, Literal

from litechat import LiteAI
from litechat._codegpt._prompts import CODE_MODIFICATION_ASSISTANT_PROMPT_FIX, CHAT_ASSISTANT_PROMPT_ORIGINAL, \
    CHAT_ASSISTANT_PROMPT
from litechat.types.hf_models import AVAILABLE_MODELS

client = LiteAI(model="Qwen/Qwen2.5-Coder-32B-Instruct")


class Message(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    conversation: Optional[bool] = False
    stream: Optional[bool] = False
    websearch: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    keep_alive: Optional[str] = "5m"


class GenerateRequest(BaseModel):
    model: Optional[str] = None
    prompt: Optional[str] = None
    conversation: Optional[bool] = False
    stream: Optional[bool] = False
    websearch: Optional[bool] = False
    assistant: Optional[str] = None
    raw: bool = False
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    context: Optional[List[int]] = None
    template: Optional[str] = None
    system: Optional[str] = None
    keep_alive: Optional[str] = "5m"


class ChatCompletionMessage(BaseModel):
    role: Literal["system", "user", "assistant", "function", "tool"]
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    user: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


def process_messages(messages):
    um = []
    for m in messages:
        if m.role == 'system':
            if 'code modification assistant' in m.content:
                content = CODE_MODIFICATION_ASSISTANT_PROMPT_FIX
            elif 'You are an AI programming assistant' in m.content:
                content = CHAT_ASSISTANT_PROMPT
            else:
                content = m.content
            um.append({'role': "system", 'content': content})
        elif m.role == "user":
            user_request = {"role": m.role, "content": m.content}

    um.append(user_request)
    return um


class UnifiedAIAPI(FastAPI):
    def __init__(self):
        super().__init__(title="Unified AI API")
        self.ai_models = AVAILABLE_MODELS
        self.conversation_id = None
        self.setup_routes()

    async def _process_stream(self, generator):
        """Helper method to process synchronous generator in async context"""
        for chunk in generator:
            yield chunk
            await asyncio.sleep(0)

    def setup_routes(self):

        @self.get("/api/tags")
        async def list_models():
            """List available models"""
            def get_json(model):
                return {
                    "name": model,
                    "modified_at": str(time.time()),
                    "size": 32,
                    "digest": "dummy",
                    "details": {
                        "family": "unk",
                        "parameter_size": "unk"
                    }
                }
            models = [get_json(model) for model in self.ai_models]
            return {"models": models}


        @self.post("/v1/chat/completions")
        async def create_chat_completion(request: ChatCompletionRequest):
            # Convert OpenAI-style messages to Ollama format
            ollama_messages = [
                Message(
                    role=msg.role,
                    content=msg.content,
                    tool_calls=msg.tool_calls
                ) for msg in request.messages
            ]

            # Create Ollama-style chat request
            ollama_request = ChatRequest(
                model=request.model,
                messages=ollama_messages,
                stream=request.stream,
                options={
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "max_tokens": request.max_tokens,
                    "presence_penalty": request.presence_penalty,
                    "frequency_penalty": request.frequency_penalty
                },
                tools=request.tools
            )

            if request.stream:
                return StreamingResponse(
                    self._stream_chat_completion(ollama_request),
                    media_type="text/event-stream"
                )

        @self.get("/v1/models")
        async def list_models():
            return {
                "object": "list",
                "data": [
                    {
                        "id": model,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "organization",
                        "permission": [],
                        "root": model,
                        "parent": None
                    }
                    for model in self.ai_models
                ]
            }

    async def _stream_chat(self, request: ChatRequest, messages: List[Message]):
        self.update_convseration_id(messages)

        updated_messages = process_messages(messages)
        for chunk in client.chat.completions.create(messages=updated_messages,
                                                    model=request.model,
                                                    stream=True,
                                                    conversation_id=self.conversation_id):
            word = chunk.choices[0].delta.content
            await asyncio.sleep(0)
            response = {
                "model": request.model,
                "created_at": str(uuid.uuid4()),
                "message": {"role": "assistant", "content": word},
                "done": False
            }
            yield f"data: {json.dumps(response)}\n\n"

    async def _stream_chat_completion(self, request: ChatRequest):
        async for chunk in self._stream_chat(request, request.messages):
            data = json.loads(chunk.replace("data: ", ""))

            if data["done"]:
                break

            yield_res = f"""data: {json.dumps({
                'id': f"chatcmpl-{int(time.time())}",
                'object': 'chat.completion.chunk',
                'created': int(time.time()),
                'model': request.model,
                'choices': [{
                    'index': 0,
                    'delta': {
                        'role': 'assistant',
                        'content': data['message']['content'].replace("<python_outer_tag>", "```")
                    },
                    'finish_reason': None
                }]
            })}\n\n"""
            yield yield_res

    def update_convseration_id(self, messages):
        roles = [m.role for m in messages]
        if self.conversation_id is None:
            self.conversation_id = str(uuid.uuid4())
        else:
            if 'assistant' not in roles:
                self.conversation_id = str(uuid.uuid4())


def litechat_codegpt_server(
    host: str = "0.0.0.0",
    port: int = 11436
):
    app = UnifiedAIAPI()
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # Run the server on localhost, port 11436
    litechat_codegpt_server()
