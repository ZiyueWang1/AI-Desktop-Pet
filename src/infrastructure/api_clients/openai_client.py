"""
OpenAI API Client
Handles communication with OpenAI API
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI


class OpenAIClient:
    """OpenAI API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment variable
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key is required. Set it in settings or OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dicts with "role" and "content"
            model: Model name (default: gpt-4o-mini)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Create embedding for text
        
        Args:
            text: Text to embed
            model: Embedding model name
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"OpenAI embedding error: {str(e)}")

