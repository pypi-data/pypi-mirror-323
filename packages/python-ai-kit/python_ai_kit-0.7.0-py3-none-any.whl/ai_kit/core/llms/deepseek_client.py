from openai import AsyncOpenAI
from ai_kit.config import LiteLLMConfig
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Model must be in both
ALLOWED_DEEPSEEK_MODELS = ["r1"]

# Must be in both LiteLLMConfig.SUPPORTED_REASONING_MODELS and ALLOWED_DEEPSEEK_MODELS
ALLOWED_MODELS = [
    m for m in LiteLLMConfig.SUPPORTED_REASONING_MODELS if m in ALLOWED_DEEPSEEK_MODELS
]


class DeepSeekClient:
    def __init__(self, model: str = "r1"):
        self.model = model
        self._validate_model(self.model, LiteLLMConfig.SUPPORTED_REASONING_MODELS)
        self.mapped_model = self._get_model_name(self.model)
        self.temperature = 0

        # Check for required API keys
        if self.model in LiteLLMConfig.REQUIRED_API_KEYS:
            required_key = LiteLLMConfig.REQUIRED_API_KEYS[self.model]
            if not os.environ.get(required_key):
                raise ValueError(
                    f"Missing required API key: {required_key} for model {self.model}"
                )

        # pass in api key to the client
        self.client = AsyncOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
        )

    def _validate_model(self, model: str, supported_models: List[str]) -> None:
        """Validate that the model is supported."""
        if model not in supported_models:
            raise ValueError(
                f"Model {model} not supported. Choose from: {', '.join(supported_models)}"
            )

    def _get_model_name(self, model: str) -> str:
        """Get the actual model name from the colloquial name."""
        return LiteLLMConfig.MODEL_MAPPINGS.get(model, model)

    async def reasoning_completion(
        self,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        thoughts_only: bool = False,
    ):
        response = await self.client.chat.completions.create(
            model=self.mapped_model,
            messages=messages,
            temperature=self.temperature,
            stream=stream,
        )
        if not stream and thoughts_only:
            raise ValueError("thoughts_only is only supported for streaming responses")
        try:
            if stream:
                async def response_generator():
                    async for chunk in response:
                        # If content is not None, we're done thinking
                        if thoughts_only and chunk.choices[0].delta.content is not None: break
                        yield {
                            "choices": [
                                {
                                    "delta": {
                                        "content": chunk.choices[0].delta.content,
                                        "reasoning_content": (
                                            chunk.choices[0].delta.reasoning_content
                                            if hasattr(
                                                chunk.choices[0].delta,
                                                "reasoning_content",
                                            )
                                            else ""
                                        ),
                                    }
                                }
                            ],
                        }

                return response_generator() # return instance of generator

            return {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content,
                            "reasoning_content": response.choices[
                                0
                            ].message.reasoning_content,
                        }
                    }
                ]
            }

        except ValueError as e:
            raise e  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")
