"""
Client-side Desktop Pet Application
Uses API client to communicate with backend server
"""
import os
import sys
import signal
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Use absolute imports (compatible with direct run and package import)
try:
    from .infrastructure.config_manager import ConfigManager
    from .presentation.floating_window import FloatingWindow
    from .presentation.chat_widget import ChatUI
    from .presentation.setup_window import SetupWindow
    from .presentation.personality_setup_window import PersonalitySetupWindow
    from .api_client import APIClient
except ImportError:
    # If relative import fails, use absolute import
    from infrastructure.config_manager import ConfigManager
    from presentation.floating_window import FloatingWindow
    from presentation.chat_widget import ChatUI
    from presentation.setup_window import SetupWindow
    from presentation.personality_setup_window import PersonalitySetupWindow
    from api_client import APIClient


class DesktopPetApp:
    """Desktop pet application main class (client-side)"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config_manager = ConfigManager()
        self.window = None
        self.setup_window = None
        self.chat_ui = None
        self.setup_ui = None
        
        # Initialize API client
        api_url = os.getenv("API_BASE_URL", "http://localhost:8080")
        self.api_client = APIClient(base_url=api_url)
        
        # Check backend health
        if not self.api_client.health_check():
            print(f"⚠ Warning: Backend API at {api_url} is not available.")
            print("   Make sure the backend server is running.")
            print("   You can set API_BASE_URL environment variable to change the URL.")
        
        # Conversation history (loaded from backend)
        self.conversation_history = []
        
        # Proactive conversation tracking
        self.last_user_message_time = datetime.now()
        self.proactive_interval_minutes = 10
        self.proactive_timer = None
        
        # Enable Ctrl+C to quit
        signal.signal(signal.SIGINT, self._handle_sigint)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)
    
    def _handle_sigint(self, signum, frame):
        """Handle SIGINT (Ctrl+C) signal"""
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        # Check if this is the first run
        if self.config_manager.check_first_run():
            # First run: show personality setup interface
            self._show_personality_setup()
        else:
            # Not first run: show main window directly
            self._show_main_window()
        
        # Run the application
        sys.exit(self.app.exec())
    
    def _show_personality_setup(self):
        """Show personality setup interface in large centered window"""
        self.setup_window = SetupWindow()
        self.setup_ui = PersonalitySetupWindow()
        self.setup_ui.personality_saved.connect(self._on_personality_saved)
        self.setup_ui.window_closed.connect(self._on_setup_closed)
        self.setup_window.set_content(self.setup_ui)
        self.setup_window.show()
    
    def _show_main_window(self):
        """Show main window (chat interface)"""
        # Create window
        self.window = FloatingWindow()
        
        # Create chat interface
        self.chat_ui = ChatUI()
        self.chat_ui.message_sent.connect(self._on_message_sent)
        
        # Set content
        self.window.set_content(self.chat_ui)
        
        # Connect settings changed signal
        if hasattr(self.window, 'settings_window') and self.window.settings_window:
            self.window.settings_window.settings_changed.connect(self._on_settings_changed)
        
        # Load window position and opacity
        config = self.config_manager.load_config()
        window_config = config.get("window", {})
        self.window.move(
            window_config.get("x", 100),
            window_config.get("y", 100)
        )
        
        # Apply opacity
        opacity = config.get("opacity", 92)
        self._apply_opacity(opacity)
        
        # Load and display conversation history from backend
        self._load_and_display_history()
        
        # Show welcome message only if no history exists
        if not self.conversation_history:
            personality = self.config_manager.load_personality()
            if personality:
                welcome_msg = "Hello! I'm ready to chat with you."
            else:
                welcome_msg = "Hello! I'm your AI companion."
            
            self.chat_ui.add_message(welcome_msg, is_user=False)
            self.conversation_history.append({"role": "assistant", "content": welcome_msg})
        
        # Show window
        self.window.show()
        
        # Start proactive conversation timer
        self._start_proactive_timer()
    
    def _apply_opacity(self, opacity: int):
        """Apply window opacity"""
        if self.window:
            opacity_value = opacity / 100.0
            self.window.setWindowOpacity(opacity_value)
    
    def _on_settings_changed(self):
        """Handle settings change"""
        config = self.config_manager.load_config()
        opacity = config.get("opacity", 92)
        self._apply_opacity(opacity)
        # Note: API keys are now managed on the backend, not in client settings
    
    def _on_personality_saved(self, personality: str):
        """Callback after personality settings are saved"""
        # Save personality settings locally (for display purposes)
        self.config_manager.save_personality(personality)
        
        # Close setup window
        if self.setup_window:
            self.setup_window.close()
            self.setup_window = None
        self.setup_ui = None
        
        # Show main window
        self._show_main_window()
    
    def _on_setup_closed(self):
        """Callback when setup window is closed"""
        if self.setup_window:
            default_personality = (
                "You are a friendly and supportive AI companion. You are always positive and optimistic, "
                "providing encouragement and advice when users need it. You like to communicate in a warm and relaxed tone, "
                "and you will remember users' personal information and preferences to provide more personalized companionship."
            )
            self.config_manager.save_personality(default_personality)
            self.setup_window.close()
            self.setup_window = None
            self._show_main_window()
    
    def _on_message_sent(self, message: str):
        """Callback when user sends a message"""
        # Update last user message time
        self.last_user_message_time = datetime.now()
        
        # Reset proactive timer
        self._reset_proactive_timer()
        
        # Display user message
        self.chat_ui.add_message(message, is_user=True)
        
        # Add to local conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Show thinking indicator
        self.chat_ui.add_thinking_indicator()
        
        # Send message to backend API in background thread
        class APIWorker(QThread):
            response_ready = pyqtSignal(str)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, api_client, message):
                super().__init__()
                self.api_client = api_client
                self.message = message
            
            def run(self):
                try:
                    response = self.api_client.chat(self.message)
                    self.response_ready.emit(response)
                except ConnectionError as e:
                    self.error_occurred.emit(f"Cannot connect to backend: {str(e)}")
                except TimeoutError as e:
                    self.error_occurred.emit(f"Request timed out: {str(e)}")
                except Exception as e:
                    self.error_occurred.emit(f"Error: {str(e)}")
        
        # Create and start worker thread
        self.api_worker = APIWorker(self.api_client, message)
        self.api_worker.response_ready.connect(self._on_api_response)
        self.api_worker.error_occurred.connect(self._on_api_error)
        self.api_worker.start()
    
    def _on_api_response(self, response: str):
        """Handle API response"""
        # Remove thinking indicator
        self.chat_ui.remove_thinking_indicator()
        
        # Display AI response
        self.chat_ui.add_message(response, is_user=False)
        
        # Add to local conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep only last 20 messages locally (for display)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _on_api_error(self, error: str):
        """Handle API error"""
        self.chat_ui.remove_thinking_indicator()
        error_msg = f"Sorry, I encountered an error: {error}"
        self.chat_ui.add_message(error_msg, is_user=False)
        self.conversation_history.append({"role": "assistant", "content": error_msg})
    
    def _load_and_display_history(self):
        """Load conversation history from backend and display in chat UI"""
        try:
            # Load from backend
            history = self.api_client.get_conversation_history()
            self.conversation_history = history
            
            # Display all messages
            for msg in history:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                if content:
                    is_user = (role == "user")
                    self.chat_ui.add_message(content, is_user=is_user)
        except Exception as e:
            print(f"Warning: Failed to load conversation history: {e}")
            # Continue with empty history
    
    def _start_proactive_timer(self):
        """Start proactive conversation timer"""
        if self.proactive_timer:
            self.proactive_timer.stop()
        
        self.proactive_timer = QTimer()
        self.proactive_timer.timeout.connect(self._check_and_initiate_proactive_conversation)
        self.proactive_timer.start(self.proactive_interval_minutes * 60 * 1000)
        print(f"✓ Proactive conversation timer started (interval: {self.proactive_interval_minutes} minutes)")
    
    def _reset_proactive_timer(self):
        """Reset proactive conversation timer"""
        if self.proactive_timer:
            self.proactive_timer.stop()
            self._start_proactive_timer()
    
    def _check_and_initiate_proactive_conversation(self):
        """Check if we should initiate proactive conversation"""
        if not self.chat_ui:
            return
        
        time_since_last_message = datetime.now() - self.last_user_message_time
        
        if time_since_last_message >= timedelta(minutes=self.proactive_interval_minutes):
            if self.conversation_history:
                last_msg = self.conversation_history[-1]
                if last_msg.get("role") == "assistant" and last_msg.get("proactive", False):
                    return
            
            # Initiate proactive conversation
            self._initiate_proactive_conversation()
    
    def _initiate_proactive_conversation(self):
        """Initiate proactive conversation via API"""
        if not self.chat_ui:
            return
        
        print(f"💬 Initiating proactive conversation after {self.proactive_interval_minutes} minutes of silence")
        
        # Use API to generate proactive message
        # We'll send a special message that triggers proactive mode
        proactive_prompt = "[Generate a brief, natural proactive message to check in with the user. Keep it warm and caring, 1-2 sentences.]"
        
        class ProactiveWorker(QThread):
            message_ready = pyqtSignal(str)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, api_client, message):
                super().__init__()
                self.api_client = api_client
                self.message = message
            
            def run(self):
                try:
                    response = self.api_client.chat(self.message)
                    self.message_ready.emit(response)
                except Exception as e:
                    self.error_occurred.emit(f"Error: {str(e)}")
        
        self.proactive_worker = ProactiveWorker(self.api_client, proactive_prompt)
        self.proactive_worker.message_ready.connect(self._on_proactive_message)
        self.proactive_worker.error_occurred.connect(self._on_proactive_error)
        self.proactive_worker.start()
    
    def _on_proactive_message(self, message: str):
        """Handle proactive message"""
        self.chat_ui.add_message(message, is_user=False)
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "proactive": True
        })
        self._reset_proactive_timer()
        print(f"✓ Proactive message sent: {message[:50]}...")
    
    def _on_proactive_error(self, error: str):
        """Handle proactive conversation error"""
        print(f"✗ Proactive conversation failed: {error}")
        self._reset_proactive_timer()


def main():
    """Main function"""
    app = DesktopPetApp()
    app.run()


if __name__ == "__main__":
    main()

