"""
Echo Agent Implementation
Simple agent that echoes back the input

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from agents.agent_registry import BaseAgent
from typing import Dict, Any


class EchoAgent(BaseAgent):
    """Simple echo agent for testing"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        message = input_data.get('input', 'No input provided')
        
        return {
            'success': True,
            'echo': message,
            'agent': self.agent_id
        }
    
    def get_capabilities(self) -> list:
        """Return list of capabilities"""
        return ['echo', 'test']
