"""
API Client for Desktop Pet
Handles communication with backend API server
"""
import requests
import uuid
import json
from pathlib import Path
from typing import Optional, List, Dict
import os


class APIClient:
    """HTTP client for backend API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Backend API base URL (default: http://localhost:8080)
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8080")
        self.user_id = self._get_or_create_user_id()
        self.session = requests.Session()
        # Set timeout for requests
        self.timeout = 30
    
    def _get_or_create_user_id(self) -> str:
        """Get or create user ID (stored locally)"""
        # Try to get from environment variable first
        user_id = os.getenv("USER_ID")
        if user_id:
            return user_id
        
        # Get from local config file
        config_file = Path.home() / ".desktop-pet" / "client_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("user_id")
            except Exception:
                pass
        
        # Create new user ID
        user_id = str(uuid.uuid4())
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({"user_id": user_id}, f, indent=2)
        except Exception:
            pass  # If we can't save, just use it in memory
        
        return user_id
    
    def chat(self, message: str) -> str:
        """
        Send message to backend API and get response
        
        Args:
            message: User message text
            
        Returns:
            AI response text
            
        Raises:
            requests.RequestException: If API call fails
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "user_id": self.user_id,
                    "message": message
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to backend API at {self.base_url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to backend API timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history from backend
        
        Returns:
            List of messages in format [{"role": "user|assistant", "content": "..."}, ...]
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/conversation/{self.user_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("history", [])
        except requests.exceptions.ConnectionError:
            # If backend is not available, return empty history
            return []
        except Exception:
            return []
    
    def get_profile(self) -> Optional[Dict]:
        """
        Get user profile from backend
        
        Returns:
            User profile dict or None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/profile/{self.user_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("profile")
        except Exception:
            return None
    
    def health_check(self) -> bool:
        """
        Check if backend API is available
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

