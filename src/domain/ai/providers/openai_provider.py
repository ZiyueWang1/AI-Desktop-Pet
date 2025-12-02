"""
OpenAI Provider Implementation
"""
from typing import List, Dict
from ....infrastructure.api_clients.openai_client import OpenAIClient
from .base_provider import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.client = OpenAIClient(api_key=api_key)
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
        Generate response using OpenAI
        
        Args:
            messages: List of message dicts
            system_prompt: System instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens
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
        
        return self.client.chat_completion(
            messages=formatted_messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

