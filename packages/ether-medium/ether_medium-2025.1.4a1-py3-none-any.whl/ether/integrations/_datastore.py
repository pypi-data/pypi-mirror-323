from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import logging

class EtherDataStore(ABC):
    """Base class for database integrations"""
    
    def __init__(self, 
                 connection_params: dict,
                 logger: Optional[logging.Logger] = None):
        self._connection = None
        self._connection_params = connection_params
        self._logger = logger or logging.getLogger(__name__)
        self._is_connected = False
        
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
        
    @abstractmethod
    def setup_change_detection(self, callback: Callable) -> None:
        """Set up native change detection if available"""
        pass
        
    @property
    def supports_notifications(self) -> bool:
        """Whether this database supports native change notifications"""
        return False 