"""
Base Agent and Agent Registry
Foundation for all agents in the system

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import json
import os
import importlib
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from threading import Lock
from datetime import datetime


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


class AgentRegistry:
    """Singleton registry for agent management"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AgentRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_configs: Dict[str, Dict[str, Any]] = {}
        self._config_dir = 'config/agents'
        self._initialized = True
        self.load_agents()
    
    def load_agents(self) -> None:
        """Load agents from configuration directory"""
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir, exist_ok=True)
            return
        
        self._agents.clear()
        self._agent_configs.clear()
        
        for filename in os.listdir(self._config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self._config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)
                    
                    # Check if agent is enabled
                    if not config.get('enabled', True):
                        continue  # Skip disabled agents

                    agent_id = config.get('agent_id')
                    module_path = config.get('module')

                    if agent_id and module_path:
                        self._agent_configs[agent_id] = config

                        # Dynamically load agent class
                        try:
                            module_name, class_name = module_path.rsplit('.', 1)
                            module = importlib.import_module(module_name)
                            agent_class = getattr(module, class_name)

                            # Instantiate agent
                            agent = agent_class(
                                agent_id=agent_id,
                                name=config.get('name', agent_id),
                                description=config.get('description', ''),
                                config=config.get('config', {})
                            )

                            self._agents[agent_id] = agent
                        except Exception as e:
                            print(f"Error loading agent {agent_id}: {e}")

                except Exception as e:
                    print(f"Error reading agent config {filename}: {e}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self._agents.get(agent_id)

    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self._agents.values())

    def execute_agent(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent"""
        agent = self._agents.get(agent_id)
        if not agent:
            return {
                'success': False,
                'error': f'Agent not found: {agent_id}'
            }

        try:
            result = agent.execute(input_data)
            return {
                'success': True,
                'result': result,
                'agent_id': agent_id,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id,
                'executed_at': datetime.now().isoformat()
            }

    def reload(self) -> None:
        """Reload all agents from configuration"""
        self.load_agents()

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        agent = self._agents.get(agent_id)
        if agent:
            return agent.to_dict()
        return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents with their info"""
        agents_list = []
        for agent in self._agents.values():
            agent_dict = agent.to_dict()
            agent_dict['enabled'] = self.is_agent_enabled(agent.agent_id)
            agents_list.append(agent_dict)
        return agents_list

    def create_agent_from_json(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new agent from JSON configuration

        Args:
            agent_data: Dictionary containing agent configuration
                {
                    "agent_id": "agent_id",
                    "name": "Agent Name",
                    "description": "Agent description",
                    "module": "agents.module.ClassName",
                    "config": {...}
                }

        Returns:
            Result dictionary with success status
        """
        try:
            agent_id = agent_data.get('agent_id')
            if not agent_id:
                return {'success': False, 'error': 'Agent ID is required'}

            # Check if agent already exists
            if agent_id in self._agents:
                return {'success': False, 'error': f'Agent {agent_id} already exists'}

            # Ensure config directory exists
            os.makedirs(self._config_dir, exist_ok=True)

            # Create config file
            config_path = os.path.join(self._config_dir, f"{agent_id}.json")
            if os.path.exists(config_path):
                return {'success': False, 'error': f'Configuration file for {agent_id} already exists'}

            # Prepare configuration
            config = {
                'agent_id': agent_id,
                'name': agent_data.get('name', agent_id),
                'description': agent_data.get('description', ''),
                'module': agent_data.get('module'),
                'config': agent_data.get('config', {}),
                'enabled': True
            }

            # Write configuration file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Reload agents to include new one
            self.load_agents()

            return {
                'success': True,
                'message': f'Agent {agent_id} created successfully',
                'agent_id': agent_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create agent: {str(e)}'
            }

    def enable_agent(self, agent_id: str) -> bool:
        """Enable an agent"""
        try:
            config_path = os.path.join(self._config_dir, f"{agent_id}.json")
            if not os.path.exists(config_path):
                return False

            with open(config_path, 'r') as f:
                config = json.load(f)

            config['enabled'] = True

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            self.load_agents()
            return True
        except:
            return False

    def disable_agent(self, agent_id: str) -> bool:
        """Disable an agent"""
        try:
            config_path = os.path.join(self._config_dir, f"{agent_id}.json")
            if not os.path.exists(config_path):
                return False

            with open(config_path, 'r') as f:
                config = json.load(f)

            config['enabled'] = False

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Remove from active agents
            if agent_id in self._agents:
                del self._agents[agent_id]

            return True
        except:
            return False

    def is_agent_enabled(self, agent_id: str) -> bool:
        """Check if an agent is enabled"""
        try:
            config_path = os.path.join(self._config_dir, f"{agent_id}.json")
            if not os.path.exists(config_path):
                return False

            with open(config_path, 'r') as f:
                config = json.load(f)

            return config.get('enabled', True)
        except:
            return False