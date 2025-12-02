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
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            base_dir: Data directory path, defaults to data/ under project root
        """
        if base_dir is None:
            # Get project root directory (parent of client/src)
            # Go up: client/src/infrastructure -> client/src -> client -> project_root
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(base_dir)
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        self.config_file = self.data_dir / "config.json"
        self.personality_file = self.data_dir / "personality.json"
        self.conversation_history_file = self.data_dir / "conversation_history.json"
    
    def _load_json(self, file_path: Path, default: Dict) -> Dict:
        """Load JSON file, return default value if it doesn't exist"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default
        return default
    
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
            "gemini_model": "gemini-2.5-flash"
        }
        return self._load_json(self.config_file, default_config)
    
    def save_config(self, config: Dict) -> bool:
        """Save application configuration"""
        return self._save_json(self.config_file, config)
    
    def load_personality(self) -> Optional[str]:
        """Load personality settings, return None if it doesn't exist"""
        default = {"personality": None}
        data = self._load_json(self.personality_file, default)
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
        data = self._load_json(self.personality_file, {})
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

