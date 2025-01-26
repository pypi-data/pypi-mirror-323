"""LiteLLM client wrapper for AI Kit."""

from typing import List, Dict, Any, Optional, AsyncIterator, Union, TypedDict
from ...config import LiteLLMConfig
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# ignore pylance errors
class BaseLiteLLMClient:
    """Base client with shared functionality."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy load litellm."""
        if self._client is None:
            import litellm

            self._client = litellm
            self._client.return_response_headers = True
        return self._client

    def _validate_model(self, model: str, supported_models: List[str]) -> None:
        """Validate that the model is supported."""
        if model not in supported_models:
            raise ValueError(
                f"Model {model} not supported. Choose from: {', '.join(supported_models)}"
            )

    def _get_model_name(self, model: str) -> str:
        """Get the actual model name from the colloquial name."""
        return LiteLLMConfig.MODEL_MAPPINGS.get(model, model)


class StructuredOutputClient(BaseLiteLLMClient):
    """Client for structured output completions."""

    from pydantic import BaseModel

    def __init__(self, model: Optional[str] = None):
        super().__init__(model or LiteLLMConfig.DEFAULT_CHAT_MODEL)
        self._validate_model(self.model, LiteLLMConfig.SUPPORTED_CHAT_MODELS)
        self.mapped_model = self._get_model_name(self.model)

    def structured_output_completion(
        self, messages: List[Dict[str, str]], schema: BaseModel
    ) -> BaseModel:
        """Get a structured output completion from the model."""
        try:
            res = self.client.completion(
                model=self.mapped_model,
                messages=messages,
                response_format=schema,
            )
            try:
                return schema.model_validate_json(res.choices[0].message.content)
            except Exception as e:
                print(e)
                return res.choices[0].message.content
        except ValueError as e:
            raise e  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error in structured output completion: {str(e)}")


class ChatClient(BaseLiteLLMClient):
    """Client for chat completions."""

    def __init__(self, model: Optional[str] = None):
        super().__init__(model or LiteLLMConfig.DEFAULT_CHAT_MODEL)
        self._validate_model(self.model, LiteLLMConfig.SUPPORTED_CHAT_MODELS)
        self.mapped_model = self._get_model_name(self.model)

    async def chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Get a chat completion from the model."""
        try:
            if "model" in kwargs:
                del kwargs["model"]  # Ignore any model passed in kwargs

            response = self.client.completion(
                model=self.mapped_model, messages=messages, stream=stream, **kwargs
            )

            if stream:

                async def response_generator():
                    async for chunk in response:
                        yield {
                            "choices": [
                                {
                                    "delta": {
                                        "content": chunk.choices[0].delta.content or ""
                                    }
                                }
                            ],
                            "_response_headers": getattr(
                                chunk, "_response_headers", {}
                            ),
                        }

                return response_generator()

            return {
                "choices": [
                    {"message": {"content": response.choices[0].message.content}}
                ],
                "_response_headers": getattr(response, "_response_headers", {}),
            }

        except ValueError as e:
            raise e  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")


class ReasoningClient(BaseLiteLLMClient):
    """Client for reasoning completions."""

    def __init__(self, model: Optional[str] = None):
        super().__init__(model or LiteLLMConfig.DEFAULT_REASONING_MODEL)
        self._validate_model(self.model, LiteLLMConfig.SUPPORTED_REASONING_MODELS)
        self.mapped_model = self._get_model_name(self.model)
        self.temperature = 0  # hardcode to 0 for most deterministic reasoning

        # Check for required API keys
        if self.model in LiteLLMConfig.REQUIRED_API_KEYS:
            required_key = LiteLLMConfig.REQUIRED_API_KEYS[self.model]
            if not os.environ.get(required_key):
                raise ValueError(
                    f"Missing required API key: {required_key} for model {self.model}"
                )

    async def reasoning_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Get a completion optimized for reasoning tasks."""
        try:
            if "model" in kwargs:
                del kwargs["model"]  # Ignore any model passed in kwargs

            response = self.client.completion(
                model=self.mapped_model,
                messages=messages,
                stream=stream,
                temperature=self.temperature,
                **kwargs,
            )

            if stream:

                async def response_generator():
                    async for chunk in response:
                        yield {
                            "choices": [
                                {
                                    "delta": {
                                        "content": (
                                            chunk.choices[0].delta.content
                                            if hasattr(
                                                chunk.choices[0].delta, "content"
                                            )
                                            else ""
                                        ),
                                        # ? see: https://docs.litellm.ai/docs/providers/deepseek#reasoning-models
                                        "reasoning_content": chunk.choices[
                                            0
                                        ].message.provider_specific_fields.get(
                                            "reasoning_content"
                                        )
                                        or "",
                                    }
                                }
                            ],
                            "_response_headers": getattr(
                                chunk, "_response_headers", {}
                            ),
                        }

                return response_generator()

            return {
                "choices": [
                    {"message": {"content": response.choices[0].message.content}}
                ],
                "_response_headers": getattr(response, "_response_headers", {}),
            }

        except ValueError as e:
            raise e  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error in reasoning completion: {str(e)}")




class EmbeddingResponseData(TypedDict):
    """Data from embedding model."""
    embedding: List[float]
    index: int
    object: str = "embedding"

class EmbeddingResponse(TypedDict):
    """Response from embedding model."""

    data: List[EmbeddingResponseData]
    _response_headers: Dict[str, Any]


class EmbeddingClient(BaseLiteLLMClient):
    """Client for embeddings."""

    def __init__(self, model: Optional[str] = None):
        super().__init__(model or LiteLLMConfig.DEFAULT_EMBEDDING_MODEL)
        self._validate_model(self.model, LiteLLMConfig.SUPPORTED_EMBEDDING_MODELS)
        self.mapped_model = self._get_model_name(self.model)

    @property
    def dimension(self) -> int:
        """Get the dimension for the current model."""
        return LiteLLMConfig.MODEL_DIMENSIONS[self.model]

    async def create_embeddings(
        self, input: Union[str, List[str]]
    ) -> List[List[float]]:
        """Create embeddings for the input text(s)."""
        try:
            # Convert single string to list
            if isinstance(input, str):
                input = [input]

            response: List[EmbeddingResponseData] = self.client.embedding(
                model=self.mapped_model, input=input
            )
            return [item.get("embedding") for item in response.data]

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise Exception(f"Error creating embedding: {str(e)}")
