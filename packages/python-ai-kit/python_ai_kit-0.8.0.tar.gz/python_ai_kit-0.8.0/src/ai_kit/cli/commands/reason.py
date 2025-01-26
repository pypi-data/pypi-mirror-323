from ai_kit.core.llms.litellm_client import ReasoningClient
from ai_kit.utils import print_stream

async def reason_command(prompt: str, model: str):
    SYSTEM_PROMPT = """You are a highly capable AI assistant focused on reasoning and problem-solving. Your role is to:
1. Analyze problems carefully and break them down into manageable parts
2. Consider multiple perspectives and potential solutions
3. Provide clear, logical explanations for your reasoning
4. When given code or file references, analyze them in detail
5. Make specific, actionable recommendations
6. Always maintain a professional and helpful tone

Remember to:
- Ask clarifying questions if needed
- Cite specific examples or evidence
- Consider edge cases and limitations
- Provide concrete next steps when applicable"""

    USER_PROMPT = """Please help me reason about the following:

{prompt}

If any files are referenced using {{filepath}}, I'll analyze their contents as part of my response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT.format(prompt=prompt)}
    ]
    reasoning_client = ReasoningClient(model=model)
    response = reasoning_client.reasoning_completion(messages, stream=True)
    async for chunk in response:
        print_stream(chunk) # print to stdout for cursor agent