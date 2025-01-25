from typing import Optional, List, Union, Dict, Any, AsyncGenerator
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import time
from llama_cpp import Llama
import json
from contextlib import asynccontextmanager
import uuid
import datetime
import os
from pathlib import Path
import threading


# Pydantic models for request validation
class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, str]]]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    stop: Optional[Union[str, List[str]]] = None
    response_format: Optional[dict] = None
    n: Optional[int] = 1


class ModelManager:
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.loaded_models: Dict[str, Dict[str, Any]] = {}  # Stores both model and its config
        self.model_lock = threading.Lock()

        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models in the models directory"""
        models = []
        for file in self.models_dir.glob("*.gguf"):
            models.append({
                "id": file.name,
                "object": "model",
                "created": int(file.stat().st_mtime),
                "owned_by": "user",
                "path": str(file)
            })
        return models

    def load_model(self, model_id: str, **kwargs) -> Llama:
        """Load a model by its ID"""
        with self.model_lock:
            # If model is already loaded with same config, return it
            if model_id in self.loaded_models:
                existing_config = self.loaded_models[model_id]["config"]
                if all(existing_config.get(k) == v for k, v in kwargs.items()):
                    return self.loaded_models[model_id]["model"]
                # If config is different, we'll reload the model
                self.loaded_models.pop(model_id)

            # Find the model file
            model_path = None
            for model in self.get_available_models():
                if model["id"] == model_id:
                    model_path = model["path"]
                    break

            if not model_path:
                raise ValueError(f"Model {model_id} not found")

            # Prepare model configuration
            model_kwargs = {
                "model_path": model_path,
                "n_ctx": kwargs.pop('n_ctx', 2048),
                "n_batch": kwargs.pop('n_batch', 512),
                "chat_format": kwargs.pop('chat_format',"chatml")
            }
            # Add remaining kwargs that weren't explicitly handled
            model_kwargs.update(kwargs)

            # Load new model
            try:
                model = Llama(**model_kwargs)
                self.loaded_models[model_id] = {
                    "model": model,
                    "config": model_kwargs
                }
                return model
            except Exception as e:
                raise Exception(f"Failed to load model {model_id}: {str(e)}")


# Global model manager instance
model_manager: Optional[ModelManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global model_manager
    model_manager = ModelManager(models_dir=os.environ.get("MODELS_PATH", "/home/ntlpt59/Documents/models"))
    yield
    # Shutdown
    if model_manager:
        model_manager.loaded_models.clear()


app = FastAPI(title="LlamaCpp OpenAI-Compatible API", lifespan=lifespan)


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    if not model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    try:
        # Load requested model if not already loaded
        model_params = {
            "temperature": request.temperature if request.temperature is not None else 0.7,
            "max_tokens": request.max_tokens if request.max_tokens is not None else 200
        }

        llm = model_manager.load_model(request.model, **model_params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if request.response_format:
        response_format = {
            "type": "json_object",
            "schema": request.response_format,
        }
    else:
        response_format = None

    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        if request.stream:
            completion = llm.create_chat_completion(
                messages=messages,
                stream=True,
                response_format=response_format
            )

            async def generate_stream():
                for chunk in completion:
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )

        # Non-streaming response
        responses = []
        for _ in range(request.n or 1):
            completion = llm.create_chat_completion(
                messages=messages,
                stream=False,
                response_format=response_format
            )
            responses.append({
                "index": len(responses),
                "message": completion["choices"][0]["message"],
                "finish_reason": completion["choices"][0]["finish_reason"]
            })

        return {
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": responses,
            "usage": completion.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")


@app.get("/v1/models")
async def list_models():
    """List available models"""
    if not model_manager:
        raise HTTPException(status_code=500, detail="Model manager not initialized")

    models = model_manager.get_available_models()
    return {
        "object": "list",
        "data": models
    }


def llamacpp_server(
    models_dir: str = "/home/ntlpt59/Documents/models",
    host: str = "0.0.0.0",
    port: int = 11438,
    **model_kwargs
):
    """Start the FastAPI server"""
    os.environ["MODELS_PATH"] = models_dir
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    llamacpp_server()