"""
Base Routes Class
Base class for all route handlers

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""


from abc import ABC, abstractmethod
from core.properties_configurator import PropertiesConfigurator
from core.user_registry import UserRegistry

class BaseRoutes(ABC):

    def __init__(self):
        self._props = PropertiesConfigurator()
        self._user_registry = UserRegistry

    def register_routes(self):
        """
        Register routes - to be implemented by child classes
        """
        raise NotImplementedError("Subclasses must implement register_routes()")