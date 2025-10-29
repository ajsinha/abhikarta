"""
Base Agent and Agent Registry
Foundation for all agents in the system

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.config = config or {}
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'config': self.config,
            'capabilities': self.get_capabilities(),
            'metadata': self.metadata
        }
