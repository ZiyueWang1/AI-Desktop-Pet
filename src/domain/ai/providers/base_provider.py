"""
Base AI Provider Interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class AIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs
    ) -> str:
        """
        Generate AI response
        
        Args:
            messages: List of message dicts with "role" and "content"
            system_prompt: System prompt/instructions
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        pass

