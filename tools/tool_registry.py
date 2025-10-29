"""
Base Tool and Tool Registry
Foundation for all tools in the system including MCP tools

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import json
import os
import importlib
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from threading import Lock
from datetime import datetime


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, tool_name: str, description: str, config: Dict[str, Any] = None):
        self.tool_name = tool_name
        self.description = description
        self.config = config or {}
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema"""
        return {
            'name': self.tool_name,
            'description': self.description
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary"""
        return {
            'tool_name': self.tool_name,
            'description': self.description,
            'config': self.config,
            'schema': self.get_schema(),
            'metadata': self.metadata
        }


class MCPTool(BaseTool):
    """Tool that calls MCP server endpoints"""
    
    def __init__(self, tool_name: str, description: str, mcp_url: str, 
                 tool_config: Dict[str, Any], config: Dict[str, Any] = None):
        super().__init__(tool_name, description, config)
        self.mcp_url = mcp_url
        self.tool_config = tool_config
        self.input_schema = tool_config.get('input_schema', {})
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute MCP tool via REST call"""
        try:
            # Prepare request payload
            payload = {
                'tool': self.tool_config.get('name'),
                'arguments': kwargs
            }
            
            # Make REST call to MCP server
            response = requests.post(
                f"{self.mcp_url}/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'result': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'MCP call failed: {response.status_code}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema"""
        return {
            'name': self.tool_name,
            'description': self.description,
            'input_schema': self.input_schema
        }


class ToolRegistry:
    """Singleton registry for tool management"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ToolRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._tools: Dict[str, BaseTool] = {}
        self._tool_configs: Dict[str, Dict[str, Any]] = {}
        self._config_dir = 'config/tools'
        self._mcp_config_dir = 'config/mcp'
        self._initialized = True
        self.load_tools()
    
    def load_tools(self) -> None:
        """Load tools from configuration directories"""
        self._tools.clear()
        self._tool_configs.clear()
        
        # Load regular tools
        if os.path.exists(self._config_dir):
            self._load_regular_tools()
        
        # Load MCP tools
        if os.path.exists(self._mcp_config_dir):
            self._load_mcp_tools()
    
    def _load_regular_tools(self) -> None:
        """Load regular (non-MCP) tools"""
        for filename in os.listdir(self._config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self._config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)
                    
                    tool_name = config.get('name')
                    module_path = config.get('module')
                    
                    if tool_name and module_path:
                        self._tool_configs[tool_name] = config
                        
                        # Dynamically load tool class
                        try:
                            module_name, class_name = module_path.rsplit('.', 1)
                            module = importlib.import_module(module_name)
                            tool_class = getattr(module, class_name)
                            
                            # Instantiate tool
                            tool = tool_class(
                                tool_name=tool_name,
                                description=config.get('description', ''),
                                config=config.get('config', {})
                            )
                            
                            self._tools[tool_name] = tool
                        except Exception as e:
                            print(f"Error loading tool {tool_name}: {e}")
                
                except Exception as e:
                    print(f"Error reading tool config {filename}: {e}")
    
    def _load_mcp_tools(self) -> None:
        """Load MCP tools"""
        for filename in os.listdir(self._mcp_config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self._mcp_config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)
                    
                    mcp_name = config.get('name')
                    mcp_url = config.get('mcp_url', 'http://localhost:8000')
                    tool_description = config.get('tool_description', {})
                    
                    # Create MCP tools from the tool descriptions
                    for tool_config in tool_description.get('tools', []):
                        tool_name = f"{mcp_name}_{tool_config['name']}"
                        
                        tool = MCPTool(
                            tool_name=tool_name,
                            description=tool_config.get('description', ''),
                            mcp_url=mcp_url,
                            tool_config=tool_config,
                            config=config
                        )
                        
                        self._tools[tool_name] = tool
                        self._tool_configs[tool_name] = tool_config
                
                except Exception as e:
                    print(f"Error reading MCP config {filename}: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self._tools.values())
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool"""
        tool = self._tools.get(tool_name)
        if not tool:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }
        
        try:
            result = tool.execute(**kwargs)
            return {
                'success': True,
                'result': result,
                'tool_name': tool_name,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool_name': tool_name,
                'executed_at': datetime.now().isoformat()
            }
    
    def reload(self) -> None:
        """Reload all tools from configuration"""
        self.load_tools()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool information"""
        tool = self._tools.get(tool_name)
        if tool:
            return tool.to_dict()
        return None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with their info"""
        return [tool.to_dict() for tool in self._tools.values()]
    
    def get_tools_for_planner(self) -> List[Dict[str, Any]]:
        """Get tool schemas for planner"""
        return [tool.get_schema() for tool in self._tools.values()]

    def get_mcp_servers_status(self) -> List[Dict[str, Any]]:
        """Get status of all configured MCP servers"""
        import time
        mcp_servers = []

        if not os.path.exists(self._mcp_config_dir):
            return mcp_servers

        for filename in os.listdir(self._mcp_config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self._mcp_config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)

                    mcp_name = config.get('name', filename.replace('.json', ''))
                    mcp_url = config.get('mcp_url', 'http://localhost:8000')
                    tool_description = config.get('tool_description', {})
                    tool_count = len(tool_description.get('tools', []))

                    # Check server health
                    status = 'offline'
                    response_time = None

                    try:
                        start_time = time.time()
                        response = requests.get(
                            f"{mcp_url}/health",
                            timeout=2
                        )
                        response_time = int((time.time() - start_time) * 1000)

                        if response.status_code == 200:
                            status = 'online'
                    except:
                        status = 'offline'

                    mcp_servers.append({
                        'name': mcp_name,
                        'url': mcp_url,
                        'status': status,
                        'response_time': response_time,
                        'tool_count': tool_count,
                        'config_file': filename
                    })

                except Exception as e:
                    print(f"Error reading MCP config {filename}: {e}")

        return mcp_servers