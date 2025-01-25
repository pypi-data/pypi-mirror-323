from ai_kit.core.llms.litellm_client import StructuredOutputClient
from ai_kit.config import LiteLLMConfig
from pydantic import BaseModel, Field
from typing import Literal
from time import perf_counter
import logging

logger = logging.getLogger(__name__)

class RouterDecision(BaseModel):
    """Pydantic model for routing decision"""
    model: Literal["thinking_agent", "execution_agent"] = Field(
        description="The model to use for the task"
    )
    confidence: float = Field(
        description="The confidence in the decision from 0.0 to 1.0"
    )
    reasoning: str = Field(
        description="The reasoning behind the decision, in one sentence or less"
    )

SYSTEM_PROMPT = """
You are an intelligent router.

Analyze the user's query and select from these options:
"thinking_agent" - Use for tasks requiring internet access, writing/modifying code, complex reasoning, or research. This is the default choice for most tasks.
"execution_agent" - Use only for basic conversation, simple explanations, and queries that don't require web access or complex reasoning.

Example Routing:

1. [Testing: Need for current information]
Query: "What are the latest news headlines about AI regulation?"
{
  "model": "thinking_agent",
  "confidence": 0.98,
  "reasoning": "Requires access to current news and internet content"
}

2. [Testing: Basic conversation]
Query: "How are you doing today?"
{
  "model": "execution_agent",
  "confidence": 0.95,
  "reasoning": "Simple conversational query requiring no external data"
}

3. [Testing: New code generation]
Query: "Can you write a Python script to scrape a website and analyze the data?"
{
  "model": "thinking_agent",
  "confidence": 0.99,
  "reasoning": "Requires code generation and technical reasoning capabilities"
}

4. [Testing: Simple opinion/preference]
Query: "What's your opinion on pizza?"
{
  "model": "execution_agent",
  "confidence": 0.90,
  "reasoning": "Basic preference question requiring no context or reasoning"
}

5. [Testing: Code debugging/modification]
Query: "Can you help me debug this error in my code: TypeError: cannot concatenate str and int objects"
{
  "model": "thinking_agent",
  "confidence": 0.85,
  "reasoning": "Requires technical analysis and code modification suggestions"
}

6. [Testing: Working with provided information]
Query: "Here's my Python function - can you help me reorganize it to be more readable? [code block follows]"
{
  "model": "execution_agent",
  "confidence": 0.80,
  "reasoning": "Simple code reorganization using only provided code, no new logic needed"
}

Key routing factors:
- Route to thinking_agent if the query requires:
  * Internet access or current information
  * Writing new code or adding new functionality
  * Complex reasoning or analysis
  * Research or fact-checking
  * Technical problem-solving with missing context
  
- Route to execution_agent if the query:
  * Is basic conversation
  * Requires no external data
  * Can be answered with pre-existing knowledge
  * Only involves reorganizing/reformatting provided content
  * Is a simple preference or opinion question

Return your decision in the exact format shown in the examples above.

Output:
"""

class Router:
    def __init__(self, model: str = "gpt-4o", debug: bool = False):
        self.model = model
        self.client = StructuredOutputClient(model=model)
        self.debug = debug

    def route(self, query: str, **kwargs) -> RouterDecision:
        s = perf_counter()
        res = self.client.structured_output_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            schema=RouterDecision,
        )
        if self.debug:
            logger.info(f"Router decision: {res} in {perf_counter() - s:.2f} seconds")
        return res
