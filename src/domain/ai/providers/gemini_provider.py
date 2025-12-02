"""
Gemini Provider Implementation
"""
from typing import List, Dict
from ....infrastructure.api_clients.gemini_client import GeminiClient
from .base_provider import AIProvider


class GeminiProvider(AIProvider):
    """Gemini provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Gemini API key
            model: Model name
        """
        self.client = GeminiClient(api_key=api_key, model=model)
        self.model = model
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate response using Gemini
        
        Args:
            messages: List of message dicts
            system_prompt: System instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens (not directly supported by Gemini, but kept for compatibility)
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        # Add system prompt if provided
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        formatted_messages.extend(messages)
        
        return self.client.generate_content(
            messages=formatted_messages,
            model=self.model,
            temperature=temperature,
            **kwargs
        )

