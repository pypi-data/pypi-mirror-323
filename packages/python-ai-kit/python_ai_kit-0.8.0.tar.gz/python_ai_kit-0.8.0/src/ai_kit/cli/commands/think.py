# Standard library imports
import os
from pathlib import Path

# Third-party imports
from rich.console import Console

# Local imports
from ai_kit.cli import console_instance
from ai_kit.cli.registry import registry_instance
from ai_kit.core.llms.deepseek_client import DeepSeekClient
from ai_kit.core.llms.litellm_client import StructuredOutputClient
from ai_kit.core.router import Router, RouteRegistry, RouteDefinition
from ai_kit.utils import print_stream
from ai_kit.utils.fs import package_root, find_workspace_root
from ai_kit.utils.prompts import process_file_references, load_prompt
from ai_kit.config import CoreConfig
from ai_kit.core.index import LocalSearchIndex, QuickSearchIndex

# Constants
PROJECT_ROOT = find_workspace_root()
PACKAGE_ROOT = package_root()

# we load think from the package root (since its a system prompt)
THINK_PROMPT_PATH = f"{PACKAGE_ROOT}/system_prompts/think.md"
# we load project_rules from the workspace root (since its a user prompt)
PROJECT_RULES_PATH = f"{PROJECT_ROOT}/{CoreConfig.ROOT_DIR}/project_rules.md"


class ThinkHandler:
    def __init__(self):
        self.console: Console = console_instance
        self.client: DeepSeekClient = DeepSeekClient(model="r1")

        # Initialize router with routes
        self.route_registry = RouteRegistry()
        self._setup_routes()
        self.router = Router(route_registry=self.route_registry, model="gpt-4o")

    def _setup_routes(self):
        """Setup available routes with their conditions."""
        self.route_registry.register(
            RouteDefinition(
                name="thinking_agent",
                description="Advanced reasoning, coding, research, or tasks requiring deep analysis.",
            )
        )

        self.route_registry.register(
            RouteDefinition(
                name="execution_agent",
                description="Basic conversation or simple Q&A that doesn't require external context.",
            )
        )

    async def handle_think(self, prompt: str):
        """Main entry point for the think command processing."""
        # Pre-check for context availability
        # summary_index = QuickSearchIndex(
        #     CoreConfig.INDEX_DIR, CoreConfig.SUPPORTED_FILE_EXTENSIONS
        # )
        # has_relevant_files = summary_index.quick_keyword_match(prompt)

        # Get routing decision
        decision = self.router.route(prompt)

        # TODO figure out better way to hanlde this conditional
        # Adjust decision based on context availability
        # if decision.route == "context_agent" and not has_relevant_files:
        #     self.console.ute
        #         "[yellow]No relevant files found for context. Falling back to thinking agent.[/yellow]"
        #     )
        #     decision.route = "thinking_agent"
        #     decision.confidence = 1.0  # hardcode confidence to 1.0


        # TODO make some kind of generic, "router.execute_callback()" function and register the callbacks on the route config
        # Handle the request based on the route
        if decision.route == "thinking_agent":
            await self._handle_complex_request(prompt)
        # elif decision.route == "context_agent":
        #     await self._handle_context_request(prompt)
        else:
            self._handle_simple_request()

    def _build_system_prompt(self) -> str:
        """Construct the system prompt with dynamic content."""
        try:
            base_prompt = load_prompt(THINK_PROMPT_PATH)
        except FileNotFoundError:
            self.console.print(
                f"[red]Error:[/] Could not find think.md prompt file at {THINK_PROMPT_PATH}"
            )
            self.console.print(
                "[yellow]Hint:[/] Make sure you have initialized ai-kit with `ai-kit init`"
            )
            raise SystemExit(1)

        try:
            project_rules = load_prompt(PROJECT_RULES_PATH)
        except FileNotFoundError:
            self.console.print(
                f"[red]Error:[/] Could not find project_rules.md at {PROJECT_RULES_PATH}"
            )
            self.console.print(
                "[yellow]Hint:[/] Make sure you have initialized ai-kit with `ai-kit init`"
            )
            raise SystemExit(1)

        return base_prompt.format(
            commands=registry_instance.markdown_prompt,
            project_rules=project_rules,
        )

    async def _handle_complex_request(self, prompt: str):
        """Handle requests requiring deep thinking."""
        processed_prompt = process_file_references(prompt)
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": processed_prompt},
        ]
        with self.console.status("[bold green]Thinking..."):
            response = await self.client.reasoning_completion(
                messages=messages,
                stream=True,
                thoughts_only=True,
            )
            self.console.print("\n[bold]Thinking Process:[/bold]")
            await print_stream(response)
        print("</thinking>")

    # ! Currently unused
    async def _handle_context_request(self, prompt: str):
        """Handle requests requiring context from local files."""
        local_index = LocalSearchIndex(max_paragraph_size=2000)
        context = await local_index.get_rag_context(
            prompt, max_chunks=20, max_tokens=50000
        )
        CONTEXT_PROMPT = f"<context>{context}</context>\n<query>{prompt}</query>"
        await self._handle_complex_request(CONTEXT_PROMPT)

    def _handle_simple_request(self):
        """Handle simple requests that don't require deep thinking."""
        self.console.print(f"<thinking>I should answer the user's request</thinking>")


async def think_command(prompt: str):
    """CLI entry point for the think command."""
    handler = ThinkHandler()
    await handler.handle_think(prompt)
