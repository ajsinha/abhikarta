from abc import ABC, abstractmethod
from core.properties_configurator import PropertiesConfigurator
from core.user_registry import UserRegistry

class BaseRoutes(ABC):

    def __init__(self):
        self._props = PropertiesConfigurator()
        self._user_registry = UserRegistry