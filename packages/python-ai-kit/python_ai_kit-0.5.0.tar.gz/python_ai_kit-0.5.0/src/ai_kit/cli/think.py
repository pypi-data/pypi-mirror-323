# Standard library imports
import os
from pathlib import Path

# Third-party imports
from rich.console import Console

# Local imports
from ..cli import console_instance
from ..cli.registry import registry_instance
from ..core.llms.deepseek_client import DeepSeekClient
from ..core.router import Router, RouterDecision
from ..utils import print_stream
from ..utils.prompts import process_file_references, load_prompt

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
THINK_PROMPT_PATH = PROJECT_ROOT / "system_prompts/think.md"
PROJECT_RULES_PATH = PROJECT_ROOT / "templates/project_rules.md"

class ThinkHandler:
    def __init__(self):
        self.console: Console = console_instance
        self.router: Router = Router(debug=False)
        self.client: DeepSeekClient = DeepSeekClient(model="r1")

    async def handle_think(self, prompt: str):
        """Main entry point for the think command processing."""
        decision = self._route_request(prompt)
        
        if decision.model == "thinking_agent":
            await self._process_complex_request(prompt, decision)
        else:
            self._handle_simple_request()

    def _route_request(self, prompt: str) -> RouterDecision:
        """Get routing decision for the request."""
        return self.router.route(prompt)

    def _build_system_prompt(self) -> str:
        """Construct the system prompt with dynamic content."""
        try:
            base_prompt = load_prompt(THINK_PROMPT_PATH)
        except FileNotFoundError:
            self.console.print(f"[red]Error:[/] Could not find think.md prompt file at {THINK_PROMPT_PATH}")
            self.console.print("[yellow]Hint:[/] Make sure you have initialized ai-kit with `ai-kit init`")
            raise SystemExit(1)
            
        try:
            project_rules = load_prompt(PROJECT_RULES_PATH)
        except FileNotFoundError:
            self.console.print(f"[red]Error:[/] Could not find project_rules.md at {PROJECT_RULES_PATH}")
            self.console.print("[yellow]Hint:[/] Make sure you have initialized ai-kit with `ai-kit init`")
            raise SystemExit(1)
            
        return base_prompt.replace(
            "{{ commands }}", registry_instance.markdown_prompt
        ).replace(
            "{{ project_rules }}", project_rules
        )

    async def _process_complex_request(self, prompt: str, decision: RouterDecision):
        """Handle requests requiring deep thinking."""
        try:
            processed_prompt = process_file_references(prompt)
            messages = [
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": processed_prompt},
            ]

            print("<thinking>")
            with self.console.status("[bold green]Thinking..."):
                response = await self.client.reasoning_completion(
                    messages=messages,
                    stream=True,
                    thoughts_only=True,
                )
                self.console.print("\n[bold]Thinking Process:[/bold]")
                await print_stream(response)
            print("</thinking>")
        except Exception as e:
            self.console.print(f"[red]Error during thinking process:[/] {str(e)}")
            raise SystemExit(1)

    def _handle_simple_request(self):
        """Handle simple requests that don't require deep thinking."""
        self.console.print(f"<thinking>I should answer the user's request</thinking>")

async def think_command(prompt: str):
    """CLI entry point for the think command."""
    handler = ThinkHandler()
    await handler.handle_think(prompt)
