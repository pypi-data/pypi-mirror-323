from typing import Optional, Dict, List, Union, Iterator
from ._client import LiteAI, ChatCompletion, ChatCompletionChunk
from litechat.types.hf_models import HFChatModels

__client: Union[LiteAI, None] = None


def get_client() -> LiteAI:
    global __client
    if __client is None:
        __client = LiteAI()
    return __client


def _build_messages(messages=None, system_prompt=None, prompt=None, context=None):
    if prompt and (messages is None):
        messages = [{"role": "user", "content": prompt}]
    elif isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    if context is not None:
        messages = _build_messages(context) + messages
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    return messages


def completion(
    messages: Optional[List[Dict[str, str]]] | str = None,
    model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    system_prompt: str = "You are helpful Assistant",
    prompt: str = "",
    context: Optional[List[Dict[str, str]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    stop: Optional[List[str]] = None,
    tools=None,
    **kwargs
) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
    client = get_client()
    web_search = kwargs.pop('web_search', False)
    kwargs['web_search'] = web_search
    conversation_id = kwargs.pop('conversation_id', "")
    kwargs['conversation_id'] = conversation_id

    messages = _build_messages(system_prompt=system_prompt,
                               prompt=prompt,
                               context=context,
                               messages=messages)
    return client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        **kwargs
    )


def genai(
    messages: Optional[List[Dict[str, str]]] | str = None,
    model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    system_prompt: str = "You are helpful Assistant",
    prompt: str = "",
    context: Optional[List[Dict[str, str]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    stop: Optional[List[str]] = None,
    tools=None,
    **kwargs
):
    response = completion(
        messages=messages,
        model=model,
        system_prompt=system_prompt,
        prompt=prompt,
        context=context,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        stop=stop,
        tools=tools,
        **kwargs
    )
    return response.choices[0].message.content


def pp_completion(
    messages: Optional[List[Dict[str, str]]] | str = None,
    model: HFChatModels = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    system_prompt: str = "You are helpful Assistant",
    prompt: str = "",
    context: Optional[List[Dict[str, str]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    stop: Optional[List[str]] = None,
    tools=None,
    **kwargs
):
    client = get_client()

    web_search = kwargs.pop('web_search', False)
    kwargs['web_search'] = web_search
    conversation_id = kwargs.pop('conversation_id', "")
    kwargs['conversation_id'] = conversation_id

    messages = _build_messages(system_prompt=system_prompt,
                               prompt=prompt,
                               context=context,
                               messages=messages)

    res = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=True,
        **kwargs
    )
    for x in res:
        print(x.choices[0].delta.content, end="", flush=True)
