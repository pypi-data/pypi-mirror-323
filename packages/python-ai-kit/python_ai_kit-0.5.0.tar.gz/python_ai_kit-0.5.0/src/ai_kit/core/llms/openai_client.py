from openai import AsyncOpenAI
from typing import AsyncIterator, Literal, List
from ai_kit.utils import get_text
# Supported models for different purposes
SUPPORTED_REASONING_MODELS = ["o1-mini", "o1"]
ReasoningModel = Literal["o1-mini", "o1"]

class OpenAIClient:
    def __init__(self, model: str = "gpt-4o", reasoning_model: ReasoningModel = "o1"):
        """Initialize OpenAI client.
        
        Args:
            model: Model to use for general chat/completion
            reasoning_model: Model to use for reasoning (o1-mini or o1)
            
        Raises:
            ValueError: If reasoning_model is not supported
        """
        if reasoning_model not in SUPPORTED_REASONING_MODELS:
            raise ValueError(f"Unsupported reasoning model: {reasoning_model}. Must be one of: {SUPPORTED_REASONING_MODELS}")
            
        self.client = AsyncOpenAI()
        self.model = model
        self.reasoning_model = reasoning_model

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content

    async def reason(self, prompt: str) -> str:
        """Execute reasoning request with specified model.
        
        Args:
            prompt: The prompt to reason about
            
        Returns:
            The model's response
        """
        res = await self.client.chat.completions.create(
            model=self.reasoning_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content


class OpenAIEmbeddingClient:
    def __init__(self, model: str = "text-embedding-3-small"):
        self._validate_model(model)
        self.client = AsyncOpenAI()

    def _validate_model(self, model: str):
        """Ensure the model is supported before proceeding."""
        if model not in MODEL_DIMENSIONS:
            raise ValueError(
                f"Unsupported embedding model: {model}. Must be one of: {list(MODEL_DIMENSIONS.keys())}"
            )
        self.model = model
        self.dimension = MODEL_DIMENSIONS[model]

    async def embed(self, text: str | List[str]) -> List[float]:
        """
        Embed a single string of text or list of strings of text.
        """
        response = await self.client.embeddings.create(
            input=text,
            model=self.model
        )
        if isinstance(text, str):
            return response.data[0].embedding
        else:
            return [item.embedding for item in response.data]