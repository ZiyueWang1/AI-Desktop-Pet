"""
Google Gemini API Client
Handles communication with Google Gemini API
"""
import os
from typing import List, Dict, Optional
import google.generativeai as genai


class GeminiClient:
    """Google Gemini API client"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment variable
            model: Model name (default: gemini-1.5-flash-latest)
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("Gemini API key is required. Set it in settings or GEMINI_API_KEY environment variable.")
        
        # Configure API - latest SDK versions (>=0.8.0) default to v1 API
        # If you see v1beta errors, upgrade: pip install --upgrade google-generativeai
        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.model_name = model
        self.chat_session = None  # Store chat session for multi-turn conversations
        self._available_models_cache = None  # Cache for available models
    
    def _get_available_models(self):
        """Get list of available models from API"""
        if self._available_models_cache is not None:
            return self._available_models_cache
        
        try:
            models = list(genai.list_models())
            available = []
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    model_name = m.name
                    # Remove 'models/' prefix if present
                    if model_name.startswith('models/'):
                        model_name = model_name[7:]
                    available.append(model_name)
            self._available_models_cache = available
            return available
        except Exception as e:
            print(f"Warning: Could not list available models: {e}")
            return []
    
    def generate_content(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate content using Gemini
        
        Args:
            messages: List of message dicts with "role" and "content"
            model: Model name (default: uses self.model_name)
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            if model is None:
                model = self.model_name
            
            # Extract system message and conversation history
            system_instruction = None
            chat_history = []
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    system_instruction = content
                elif role == "user":
                    chat_history.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    chat_history.append({"role": "model", "parts": [content]})
            
            # Initialize generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ['system']}
            )
            
            # Normalize model name - remove 'models/' prefix if present
            model_name = model.replace("models/", "") if model.startswith("models/") else model
            
            # Try to create model instance with error handling
            try:
                if system_instruction:
                    model_instance = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=generation_config,
                        system_instruction=system_instruction
                    )
                else:
                    model_instance = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=generation_config
                    )
            except Exception as model_error:
                # If model not found, try to find available models and use a fallback
                fallback_models = [
                    "gemini-2.5-flash",         # Current cheapest model
                    "gemini-2.0-flash-exp",     # Experimental
                    "gemini-2.0-flash",         # Stable 2.0
                    "gemini-flash-latest",      # Latest flash alias
                    "gemini-1.5-flash-latest", # Legacy latest
                ]
                
                # Try to get list of actually available models
                available_models_list = self._get_available_models()
                if available_models_list:
                    # Prefer models from the actual API list
                    for api_model in available_models_list:
                        # Try exact match first
                        if api_model == model_name or api_model.endswith(model_name.split('-')[-1]):
                            try:
                                if system_instruction:
                                    model_instance = genai.GenerativeModel(
                                        model_name=api_model,
                                        generation_config=generation_config,
                                        system_instruction=system_instruction
                                    )
                                else:
                                    model_instance = genai.GenerativeModel(
                                        model_name=api_model,
                                        generation_config=generation_config
                                    )
                                print(f"Warning: Model '{model_name}' not found, using '{api_model}' from API")
                                break
                            except:
                                continue
                
                # If still not found, try fallback list
                fallback_used = False
                for fallback in fallback_models:
                    try:
                        if system_instruction:
                            model_instance = genai.GenerativeModel(
                                model_name=fallback,
                                generation_config=generation_config,
                                system_instruction=system_instruction
                            )
                        else:
                            model_instance = genai.GenerativeModel(
                                model_name=fallback,
                                generation_config=generation_config
                            )
                        fallback_used = True
                        print(f"Warning: Model '{model_name}' not found, using fallback '{fallback}'")
                        break
                    except:
                        continue
                
                if not fallback_used:
                    # Provide helpful error message with available models
                    available_str = ", ".join(available_models_list[:5]) if available_models_list else "none found"
                    raise Exception(
                        f"Model '{model_name}' not found. "
                        f"Available models: {available_str}. "
                        f"Try updating 'gemini_model' in config.json to one of: {', '.join(fallback_models[:3])}. "
                        f"Original error: {str(model_error)}"
                    )
            
            # Handle conversation with history
            if len(chat_history) > 1:
                # Use chat mode for multi-turn conversation
                # Build history for start_chat (format: list of dicts with "role" and "parts")
                history = chat_history[:-1]  # All but the last message
                last_message = chat_history[-1]["parts"][0]  # The last user message
                
                # Start chat with history (no system_instruction parameter here)
                chat = model_instance.start_chat(history=history)
                # Send the last message
                response = chat.send_message(last_message)
            elif len(chat_history) == 1:
                # Single prompt mode (only one message)
                prompt = chat_history[0]["parts"][0]
                response = model_instance.generate_content(prompt)
            else:
                # No messages
                raise ValueError("No messages provided")
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

