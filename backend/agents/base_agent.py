"""Base agent class for agentic AI system."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""

    def __init__(self, agent_id: str, tools: Optional[List] = None):
        """
        Initialize base agent.

        Args:
            agent_id: Unique identifier for the agent
            tools: List of tools available to the agent
        """
        self.agent_id = agent_id
        self.tools = tools or []
        self.memory: List[Dict[str, Any]] = []
        self.created_at = datetime.now()

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.

        Args:
            task: Task parameters and data

        Returns:
            Result of the agent's execution
        """
        pass

    def log_action(self, action: str, result: Any, metadata: Optional[Dict] = None):
        """
        Log agent action to memory.

        Args:
            action: Description of the action
            result: Result of the action
            metadata: Additional metadata
        """
        self.memory.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'result': result,
            'metadata': metadata or {}
        })

    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve agent's memory.

        Args:
            limit: Maximum number of recent entries to return

        Returns:
            List of memory entries
        """
        if limit:
            return self.memory[-limit:]
        return self.memory

    def clear_memory(self):
        """Clear agent's memory."""
        self.memory = []

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool from the agent's toolset.

        Args:
            tool_name: Name of the tool to use
            **kwargs: Tool-specific arguments

        Returns:
            Tool execution result
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in agent's toolset")

        result = await tool.execute(**kwargs)
        self.log_action(f"Used tool: {tool_name}", result)
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, tools={len(self.tools)})"
