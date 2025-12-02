"""
Mock AI Provider - For load testing, doesn't consume API tokens
Simulates real AI call latency and CPU consumption
"""
import time
import random
from typing import List, Dict
from .base_provider import AIProvider


class MockAIProvider(AIProvider):
    """Mock provider that simulates AI calls without using real API"""
    
    def __init__(self, api_key: str = None, model: str = "mock-model", 
                 response_delay: float = 1.0, cpu_intensive: bool = True):
        """
        Initialize Mock Provider
        
        Args:
            api_key: Not used, kept for compatibility (can be None)
            model: Model name (not used)
            response_delay: Simulated response delay in seconds (default 1.0)
            cpu_intensive: If True, simulate CPU-intensive work (default True)
        """
        self.model = model
        self.response_delay = response_delay
        self.cpu_intensive = cpu_intensive
        
        # Predefined response templates (simulate real responses)
        self.response_templates = [
            "That's an interesting question! Let me think about that...",
            "I understand what you're asking. Here's my perspective:",
            "Thanks for sharing that with me. I'd like to respond by saying:",
            "That's a thoughtful point. From my experience:",
            "I appreciate you asking. My thoughts on this are:",
            "That's something I've been thinking about too. Here's what I think:",
            "I see what you mean. Let me offer this perspective:",
            "That's a great question! I believe:",
        ]
        
        # Generate some random response fragments
        self.response_parts = [
            "I think we should consider different perspectives.",
            "There are many ways to approach this.",
            "It's important to remember that everyone has their own view.",
            "I find this topic fascinating.",
            "Let's explore this together.",
            "I'm here to help you think through this.",
            "This reminds me of something important.",
            "I'd love to discuss this more with you.",
        ]
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 100,
        **kwargs
    ) -> str:
        """
        Generate mock response with simulated delay
        
        This simulates:
        1. Network latency (random 0.5-2.0 seconds)
        2. Processing time (CPU-intensive work if enabled)
        3. Realistic response length
        
        Args:
            messages: List of message dicts
            system_prompt: System prompt (not used in mock)
            temperature: Sampling temperature (not used)
            max_tokens: Maximum tokens (used to limit response length)
            **kwargs: Additional parameters
            
        Returns:
            Generated mock text response
        """
        # 1. Simulate network latency (random 0.5-2.0 seconds, like real API calls)
        network_delay = random.uniform(0.5, 2.0)
        time.sleep(network_delay)
        
        # 2. Simulate CPU-intensive processing (if enabled)
        if self.cpu_intensive:
            # Simulate AI processing time (consume CPU)
            processing_time = random.uniform(0.3, 1.5)
            start_time = time.time()
            # Do some CPU-intensive calculations
            while time.time() - start_time < processing_time:
                # Simple calculations to consume CPU
                _ = sum(i * i for i in range(1000))
        
        # 3. Generate mock response
        template = random.choice(self.response_templates)
        part = random.choice(self.response_parts)
        
        # Generate contextually relevant response based on user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Generate response (limit within max_tokens range, about 2 sentences)
        if user_message:
            # Generate simple response based on user message
            response = f"{template} {part}"
        else:
            response = f"{template} {part}"
        
        # Ensure response length is reasonable (about 50-100 words, 2 sentences)
        if len(response) > max_tokens * 2:  # Rough estimate
            response = response[:max_tokens * 2] + "..."
        
        return response

