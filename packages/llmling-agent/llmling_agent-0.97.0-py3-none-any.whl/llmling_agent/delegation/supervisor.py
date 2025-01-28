from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Protocol

from slashed import (
    CommandContext,
    CommandStore,
    OutputWriter,
    QueueOutputWriter,
    SlashedCommand,
)

from llmling_agent.log import get_logger
from llmling_agent.models.agents import ToolCallInfo
from llmling_agent.models.messages import ChatMessage
from llmling_agent.utils.tasks import TaskManagerMixin


if TYPE_CHECKING:
    from llmling_agent.delegation.pool import AgentPool
    from llmling_agent.models.agents import ToolCallInfo
    from llmling_agent.models.messages import ChatMessage

logger = get_logger(__name__)


class ListAgentsCommand(SlashedCommand):
    """List all agents in the pool with their status."""

    name = "list-agents"
    category = "pool"

    async def execute_command(
        self,
        ctx: CommandContext[PoolSupervisor],
        show_connections: bool = False,
    ):
        """List all agents and their current status.

        Args:
            ctx: Command context with supervisor
            show_connections: Whether to show agent connections
        """
        supervisor = ctx.get_data()
        header = "\nAvailable Agents:"
        await ctx.output.print(header)
        await ctx.output.print("=" * len(header))

        for name in supervisor.pool.list_agents():
            agent = supervisor.pool.get_agent(name)

            # Build status info
            status = "🔄 busy" if agent.is_busy() else "⏳ idle"

            # Add connections if requested
            connections = []
            if show_connections and agent.connections.get_targets():
                connections = [a.name for a in agent.connections.get_targets()]
                conn_str = f" → {', '.join(connections)}"
            else:
                conn_str = ""

            # Add description if available
            desc = f" - {agent.description}" if agent.description else ""

            await ctx.output.print(f"{name} ({status}){conn_str}{desc}")


class InputHandler(Protocol):
    """Protocol for handling user input."""

    async def get_input(self, prompt: str) -> str:
        """Get input from user with prompt.

        Args:
            prompt: Text to show user

        Returns:
            User's input
        """
        ...


class ConsoleInputHandler:
    """Default input handler using stdlib input()."""

    async def get_input(self, prompt: str) -> str:
        """Get input using standard input() in thread."""
        return await asyncio.to_thread(input, prompt)


class PoolSupervisor(TaskManagerMixin):
    """Handles human supervision of agent pool activities."""

    def __init__(
        self,
        pool: AgentPool,
        *,
        input_handler: InputHandler | None = None,
        output_handler: OutputWriter | None = None,
    ):
        self.pool = pool
        self.human_messages: asyncio.Queue[str] = asyncio.Queue()
        self.status_updates: asyncio.Queue[str] = asyncio.Queue()
        self._running = False

        # Set up handlers (with defaults)
        self.input_handler = input_handler or ConsoleInputHandler()
        self.output_handler = output_handler or QueueOutputWriter(self.status_updates)

        # Set up command system
        self.output = QueueOutputWriter(self.status_updates)
        self.commands = CommandStore()
        # Register commands would go here

    async def start(self):
        """Start supervision."""
        if self._running:
            return

        self._running = True

        # Start monitoring tasks
        self.create_task(self._monitor_human_input(), name="input_monitor", priority=0)
        self.create_task(self._print_status(), name="status_printer", priority=1)
        # Connect to pool's agents
        for agent in self.pool.agents.values():
            agent.message_sent.connect(self._handle_message)
            agent.tool_used.connect(self._handle_tool)

        await self.output_handler.print(
            "Supervision started.\n"
            "Usage:\n"
            "  @agent /command      - Execute command for specific agent\n"
            "  @agent message       - Send message to specific agent\n"
            'Type "@agent /help" for available commands.'
        )

    async def stop(self):
        """Stop supervision."""
        self._running = False

        # Disconnect from agents
        for agent in self.pool.agents.values():
            agent.message_sent.disconnect(self._handle_message)
            agent.tool_used.disconnect(self._handle_tool)

        # Cancel tasks
        await self.cleanup_tasks()

    async def _handle_message(self, message: ChatMessage):
        """Handle messages from supervised agents."""
        await self.output_handler.print(f"Agent {message.name}: {message.content}")

    async def _handle_tool(self, tool_call: ToolCallInfo):
        """Handle tool usage from supervised agents."""
        await self.output_handler.print(
            f"Tool used: {tool_call.tool_name}({tool_call.args})"
        )

    async def _handle_command(self, cmd: str):
        """Handle agent commands and messages."""
        if not cmd.startswith("@"):
            await self.output_handler.print("Usage: @agent <message or /command>")
            return

        parts = cmd[1:].split(maxsplit=1)
        if len(parts) < 2:  # noqa: PLR2004
            await self.output_handler.print("Usage: @agent_name <message or /command>")
            return

        agent_name, message = parts
        if agent_name not in self.pool.agents:
            await self.output_handler.print(f"Agent {agent_name} not found")
            return

        agent = self.pool.get_agent(agent_name)
        try:
            if message.startswith("/"):
                # Create view just for this command
                await self.commands.execute_command_with_context(
                    message[1:],
                    context=agent.context,
                    output_writer=self.output,
                    metadata={"supervision": True},
                )
            else:
                # Regular message to agent
                await agent.run(message)
        except Exception as e:  # noqa: BLE001
            await self.output_handler.print(f"Error: {e}")

    async def _monitor_human_input(self):
        """Monitor for human input."""
        print("\nSupervision active. Use @agent_name to interact with agents.")

        while self._running:
            try:
                msg = await self.input_handler.get_input("Supervisor > ")
                if msg.strip().lower() == "exit":
                    await self.stop()
                    break
                await self.human_messages.put(msg)
                await self._handle_command(msg.strip())
            except asyncio.CancelledError:
                break

    async def _print_status(self):
        """Print status updates."""
        while self._running:
            try:
                status = await self.status_updates.get()
                print(f"\nStatus: {status}")
            except asyncio.CancelledError:
                break
