from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseLLM(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        memory: Optional[List[Dict]] = None,
    ) -> str:
        pass