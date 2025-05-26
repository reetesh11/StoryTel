from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent's main logic"""
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        return True

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle any errors that occur during execution"""
        return {"error": str(error), "status": "failed"} 