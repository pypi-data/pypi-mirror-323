from ai_kit.core.llms.litellm_client import ReasoningClient
from duckduckgo_search import DDGS
from typing import Dict, Any, List

# Manager needs to take the response and 'route' it to the right place/with the right prompt
# Manager:
# - takes the response and routes it to the right place/with the right prompt
# - handles memory
# - handles tool usage and retrieval
# - modes:
#   - init chat
#   - conversation (pass through)
#   - challenge
#   - etc.

# Prompt Output Structure
# the origina task (passed in)
# the data (retrieved through tools)
# the instructions (the prompt to the LLM)

# This model will be o1 mini to start


class Modes:
    def init(self, task: str, flag: bool):
        """Initialize the mode"""
        flag = True  # initalize
        return task

    def conversation(self, task: str):
        """Conversation mode"""
        CONVERSATION_PROMPT = """
        Answer the user's question as best as you can, without using any tools. Be concise but elaborate if they ask.
        <user_input>
        {{user_input}}
        </user_input>
        """
        return CONVERSATION_PROMPT.format(user_input=task)

    def challenge(self, task: str):
        """Challenge mode"""
        CHALLENGE_PROMPT = """
        You are a challenge AI. You are designed to challenge the user's request. 
        - Be skeptical of the user's request
        - Don't immediately comply with the user's request
        - If the user's request is not clear, ask for clarification
        - Don't assume the user is always right. If you have a better idea, suggest it.
        <task>
        {{task}}
        </task>
        """
        return CHALLENGE_PROMPT.format(task=task)

    def think(self, task: str):
        pass

    def return_output(self, task: str):
        pass


PROMPT_OUTPUT_STRUCTURE = """
<task>{{task}}</task>
<context>{{context}}</context>
<instructions>{{instructions}}</instructions>
"""

# TODO upate this with a humanlike prompt (give ex agent a name and this one a name)
BASE_PROMPT = """
I am Ada, your AI development partner. I specialize in helping developers write, understand, and improve their code. I combine deep technical knowledge with clear communication to provide practical, actionable assistance.

I work closely with Eva, our execution AI model, who has these abilities:
- Reading and writing files
- Searching the codebase
- Running commands

My role is to analyze your request and prepare clear, structured instructions for Eva. I'll format my response using this structure:
{{PROMPT_OUTPUT_STRUCTURE}}

Your task for me to analyze is:
{{task}}
"""


# The manager will take the response and pass it to the next step
class Manager:
    def __init__(self, base_model: str = "o1-mini", reasoning_model: str = "o1-mini"):
        self.is_init = False  # This is used to determine if the manager is in init mode
        # This client it used for intake, routing, and output
        self.base_client = ReasoningClient(model=base_model)
        # This client is used for complex reasoning
        self.reasoning_client = ReasoningClient(model=reasoning_model)

    async def web_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Execute the web search request."""
        ddgs = DDGS()
        return ddgs.text(query, max_results=max_results)

    async def think(self, messages: List[Dict[str, str]]):
        """Use the reasoning client to think about the task."""
        return await self.reasoning_client.reasoning_completion(messages)

    async def run(self, task: str):
        """Run the task."""
        messages = [
            {
                "role": "system",
                "content": """I am Ada, your AI development partner. I specialize in helping developers write, understand, and improve their code. I combine deep technical knowledge with clear communication to provide practical, actionable assistance.

My approach:
1. I analyze problems thoroughly before suggesting solutions
2. I explain my reasoning clearly and concisely
3. I provide specific, contextual examples when helpful
4. I focus on best practices and maintainable code
5. I'm direct but friendly in my communication

When you share code or files with me using {{filepath}}, I'll carefully analyze them and provide targeted assistance."""
            },
            {"role": "user", "content": task},
        ]
        return await self.reasoning_client.reasoning_completion(messages)
