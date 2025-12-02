"""
Configuration management module
Handles read/write operations for application configuration and personality settings
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    """Configuration manager, encapsulates JSON file read/write operations"""
    
    def __init__(self, base_dir: Optional[str] = None, fallback_dir: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            base_dir: Data directory path, defaults to data/ under project root
            fallback_dir: Fallback directory path for reading configs (e.g., global data dir)
        """
        if base_dir is None:
            # Get project root directory (parent of src)
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(base_dir)
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Set fallback directory (for reading only, not writing)
        self.fallback_dir = Path(fallback_dir) if fallback_dir else None
        
        self.config_file = self.data_dir / "config.json"
        self.personality_file = self.data_dir / "personality.json"
        self.conversation_history_file = self.data_dir / "conversation_history.json"
    
    def _load_json(self, file_path: Path, default: Dict, fallback_path: Optional[Path] = None) -> Dict:
        """
        Load JSON file, return default value if it doesn't exist
        If file doesn't exist and fallback_path is provided, try loading from fallback_path
        """
        # Try primary path first
        primary_data = None
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    primary_data = json.load(f)
                    # If primary file has valid data, use it
                    if primary_data:
                        return primary_data
            except (json.JSONDecodeError, IOError):
                pass
        
        # Try fallback path if provided (when primary doesn't exist or is empty/invalid)
        if fallback_path and fallback_path.exists():
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    fallback_data = json.load(f)
                    # Merge fallback data with primary data if primary exists but is empty
                    if primary_data is None or not primary_data:
                        return fallback_data
                    # If primary exists but missing important keys, merge with fallback
                    elif isinstance(primary_data, dict) and isinstance(fallback_data, dict):
                        merged = fallback_data.copy()
                        merged.update(primary_data)  # Primary overrides fallback
                        return merged
                    return fallback_data
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return primary data if it exists, otherwise default
        return primary_data if primary_data is not None else default
    
    def _save_json(self, file_path: Path, data: Dict) -> bool:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def load_config(self) -> Dict:
        """Load application configuration"""
        default_config = {
            "window": {
                "x": 100,
                "y": 100,
                "width": 300,
                "height": 400
            },
            "theme": "light",
            "opacity": 92,
            "user_avatar": None,
            "ai_avatar": None,
            "ai_provider": "gemini",  # "openai", "claude", or "gemini"
            "openai_api_key": None,
            "claude_api_key": None,
            "gemini_api_key": None,
            "openai_model": "gpt-4o-mini",
            "claude_model": "claude-3-5-sonnet-20241022",
            "gemini_model": "gemini-2.5-flash",
            "max_tokens": 250  # Maximum tokens for AI response (controls response length)
        }
        fallback_path = None
        if self.fallback_dir:
            fallback_path = self.fallback_dir / "config.json"
        
        config = self._load_json(self.config_file, default_config, fallback_path)
        
        # If primary config exists but has no API keys, merge with fallback
        if self.fallback_dir and fallback_path and fallback_path.exists():
            fallback_config = None
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    fallback_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
            
            if fallback_config:
                # Merge: fallback provides defaults, primary overrides
                merged = fallback_config.copy()
                merged.update(config)  # Primary overrides fallback
                # But if primary has null API keys and fallback has real ones, use fallback's
                for key in ['openai_api_key', 'claude_api_key', 'gemini_api_key']:
                    if (not config.get(key) or config.get(key) is None) and fallback_config.get(key):
                        merged[key] = fallback_config[key]
                return merged
        
        return config
    
    def save_config(self, config: Dict) -> bool:
        """Save application configuration"""
        return self._save_json(self.config_file, config)
    
    def load_personality(self) -> Optional[str]:
        """Load personality settings, return None if it doesn't exist"""
        default = {"personality": None}
        fallback_path = None
        if self.fallback_dir:
            fallback_path = self.fallback_dir / "personality.json"
        data = self._load_json(self.personality_file, default, fallback_path)
        return data.get("personality")
    
    def save_personality(self, personality: str) -> bool:
        """Save personality settings"""
        data = {"personality": personality}
        return self._save_json(self.personality_file, data)
    
    def load_character_config(self) -> Dict:
        """Load detailed character configuration"""
        default = {
            "personality": "",
            "backstory": "",
            "traits": "",
            "preferences": "",
            "output_example": "",
            "user_profile": "",
            "worldview_background": "",
            "worldview_setting": "",
            "notes": ""
        }
        fallback_path = None
        if self.fallback_dir:
            fallback_path = self.fallback_dir / "personality.json"
        data = self._load_json(self.personality_file, {}, fallback_path)
        # Support both old format (just "personality" string) and new format
        if "personality" in data and isinstance(data["personality"], str) and len(data) == 1:
            # Old format - migrate to new format
            default["personality"] = data["personality"]
            return default
        # Merge with defaults to ensure all fields exist
        result = default.copy()
        result.update(data)
        return result
    
    def save_character_config(self, config: Dict) -> bool:
        """Save detailed character configuration"""
        return self._save_json(self.personality_file, config)
    
    def check_first_run(self) -> bool:
        """Check if this is the first run (personality file doesn't exist)"""
        return not self.personality_file.exists()
    
    def update_window_position(self, x: int, y: int):
        """Update window position"""
        config = self.load_config()
        config["window"]["x"] = x
        config["window"]["y"] = y
        self.save_config(config)
    
    def update_window_size(self, width: int, height: int):
        """Update window size"""
        config = self.load_config()
        config["window"]["width"] = width
        config["window"]["height"] = height
        self.save_config(config)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider
        
        Args:
            provider: "openai" or "claude"
            
        Returns:
            API key string or None
        """
        config = self.load_config()
        key_name = f"{provider}_api_key"
        # First try config file
        api_key = config.get(key_name)
        if api_key and api_key.strip():  # Check if not empty
            return api_key.strip()
        # Fallback to environment variable
        env_key = f"{provider.upper()}_API_KEY"
        env_value = os.getenv(env_key)
        if env_value and env_value.strip():
            return env_value.strip()
        return None
    
    def save_api_key(self, provider: str, api_key: str) -> bool:
        """
        Save API key for a provider
        
        Args:
            provider: "openai" or "claude"
            api_key: API key string
        """
        config = self.load_config()
        key_name = f"{provider}_api_key"
        config[key_name] = api_key
        return self.save_config(config)
    
    def get_ai_provider(self) -> str:
        """Get current AI provider"""
        config = self.load_config()
        return config.get("ai_provider", "openai")
    
    def set_ai_provider(self, provider: str) -> bool:
        """Set AI provider"""
        config = self.load_config()
        config["ai_provider"] = provider
        return self.save_config(config)
    
    def get_model(self, provider: str) -> str:
        """Get model name for provider"""
        config = self.load_config()
        model_key = f"{provider}_model"
        default_models = {
            "openai": "gpt-4o-mini",
            "claude": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-pro"
        }
        return config.get(model_key, default_models.get(provider, ""))
    
    def set_model(self, provider: str, model: str) -> bool:
        """Set model name for provider"""
        config = self.load_config()
        model_key = f"{provider}_model"
        config[model_key] = model
        return self.save_config(config)
    
    def get_max_tokens(self) -> int:
        """Get max tokens setting for AI responses"""
        config = self.load_config()
        return config.get("max_tokens", 250)
    
    def set_max_tokens(self, max_tokens: int) -> bool:
        """Set max tokens for AI responses"""
        config = self.load_config()
        config["max_tokens"] = max_tokens
        return self.save_config(config)
    
    def load_conversation_history(self) -> list:
        """
        Load conversation history from JSON file
        Returns list of messages in format: [{"role": "user|assistant", "content": "..."}, ...]
        """
        default = {"history": []}
        data = self._load_json(self.conversation_history_file, default)
        history = data.get("history", [])
        
        # Ensure we only keep last 20 messages
        if len(history) > 20:
            history = history[-20:]
        
        return history
    
    def save_conversation_history(self, history: list) -> bool:
        """
        Save conversation history to JSON file
        Keeps only last 20 messages to avoid context overflow
        
        Args:
            history: List of messages in format: [{"role": "user|assistant", "content": "..."}, ...]
        """
        # Ensure we only keep last 20 messages
        if len(history) > 20:
            history = history[-20:]
        
        data = {"history": history}
        return self._save_json(self.conversation_history_file, data)

