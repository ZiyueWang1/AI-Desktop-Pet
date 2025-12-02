"""
Claude Provider Implementation
"""
from typing import List, Dict
from ....infrastructure.api_clients.claude_client import ClaudeClient
from .base_provider import AIProvider


class ClaudeProvider(AIProvider):
    """Claude provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude provider
        
        Args:
            api_key: Claude API key
            model: Model name
        """
        self.client = ClaudeClient(api_key=api_key)
        self.model = model
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Generate response using Claude
        
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
        
        return self.client.create_message(
            messages=formatted_messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

