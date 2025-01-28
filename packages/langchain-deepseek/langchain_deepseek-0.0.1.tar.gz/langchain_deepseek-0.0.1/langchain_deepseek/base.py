import inspect
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Mapping,
    Tuple
)

from langchain_core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream
)

from langchain_core.messages import (
    BaseMessage
)

from langchain_core.outputs import (
    ChatResult,
    ChatGeneration
)

from langchain_core.callbacks import (
    CallbackManagerForLLMRun
)

from langchain_community.adapters.openai import (
    convert_message_to_dict,
    convert_dict_to_message
)

from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

from .api import RestAPI


class ChatDeepSeekAI(BaseChatModel):
    """`DeepSeek` Chat large language models API.
    
    """

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"deepseek_api_key": "DEEPSEEK_API_KEY"}

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Return"""
        return ["langchain", "chat_models", "DeepSeek"]

    @property
    def lc_attributes(self) -> Dict[str, Any]:
        attributes: Dict[str, Any] = {}
        return attributes

    @property
    def _llm_type(self) -> str:
        """Return the type of chat model."""
        return "DeepSeekAI"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {**{"model_name": self.model}, **self._default_params}

    @property
    def _default_params(self) -> Dict[str, Any]:
        params = {
            "model": self.model,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            # **self.model_kwargs
        }
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        return params

    """deepseek client"""
    client: Any = Field(default=None, exclude=True)
    """model name use"""
    model: str = Field(default="deepseek-chat")
    api_key: Optional[str] = Field(default=None, exclude=True)
    base_url: Optional[str] = Field(default=None)
    temperature: Optional[float] = Field(default=1)
    top_p: Optional[float] = Field(default=1)
    request_id: Optional[str] = Field(default=None)
    max_tokens: Optional[int] = Field(default=2048)
    streaming: Optional[bool] = Field(default=False)
    n: Optional[int] = Field(default=1)
    response_format: Dict[str, str] = Field(default={"type": "text"})
    frequency_penalty: Optional[int] = Field(default=0)
    presence_penalty: Optional[int] = Field(default=0)
    tools: Any = Field(default=None)
    tool_choice: Optional[str] = Field(default="none")
    logprobs: Optional[bool] = Field(default=False)
    top_logprobs: Optional[int] = Field(default=None)

    @classmethod
    def filter_model_kwargs(cls):
        """
        """
        return [
            "model",
            "frequency_penalty",
            "max_tokens",
            "presence_penalty",
            "response_format",
            "stop",
            "stream",
            "temperature",
            "top_p",
            "tools",
            "tool_choice",
            "logprobs",
            "top_logprobs",
            "request_id"
        ]

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs: Any
    ) -> ChatResult:
        should_stream = stream if stream is not None else self.streaming
        if should_stream:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)
        message_dict, params = self._create_message_dicts(messages, stop)
        response = self.completion_with_retry(
            message_dict=message_dict,
            run_manager=run_manager,
            params=params
        )
        return self._create_chat_result(response)

    def completion_with_retry(
            self, message_dict=None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs
    ):
        params = kwargs["params"]
        params.update({"messages": message_dict})
        try:
            self.client = RestAPI(base_url=self.base_url, api_key=self.api_key)
            reply = self.client.action_post(request_path=f"chat/completions", **params)
        except Exception as e:
            raise e
        return reply

    def _create_chat_result(self, response):
        generations = []
        id = response.get("id")
        if not isinstance(response, dict):
            response = response.dict()
        for res in response["choices"]:
            message_dict = res["message"]
            message = convert_dict_to_message(message_dict)
            generation_info = dict(finish_reason=res.get("finish_reason"))
            gen = ChatGeneration(
                message=message,
                generation_info=generation_info,
            )
            generations.append(gen)
        token_usage = response.get("usage", {})
        llm_output = {
            "id": id,
            "created": response.get("created"),
            "token_usage": token_usage,
            "model_name": self.model,
        }
        return ChatResult(generations=generations, llm_output=llm_output)

    def _create_message_dicts(
            self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params = self.get_model_kwargs()
        params.update({"stream": False})
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params.update({"stop": stop})
        message_dicts = [convert_message_to_dict(message) for message in messages]
        # 传递prompt
        params.update({"messages": message_dicts})
        return message_dicts, params

    def get_model_kwargs(self):
        attrs = {}
        for cls in inspect.getmro(self.__class__):
            attrs.update(vars(cls))
        attrs.update((vars(self)))
        return {
            attr: value for attr, value in attrs.items() if attr in self.__class__.filter_model_kwargs() and value is not None
        }
