"""
Claude API Client
Handles communication with Anthropic Claude API
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic


class ClaudeClient:
    """Claude API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client
        
        Args:
            api_key: Claude API key. If None, will try to get from environment variable
        """
        if api_key is None:
            api_key = os.getenv("CLAUDE_API_KEY")
        
        if not api_key:
            raise ValueError("Claude API key is required. Set it in settings or CLAUDE_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=api_key)
        self.api_key = api_key
    
    def create_message(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Create message (chat completion)
        
        Args:
            messages: List of message dicts with "role" and "content"
            model: Model name (default: claude-3-5-sonnet-20241022)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            # Convert messages format for Claude API
            # Claude expects system message separately and messages without system role
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    # Claude uses "user" and "assistant" roles
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else "",
                messages=claude_messages,
                **kwargs
            )
            
            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

