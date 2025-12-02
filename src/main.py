"""
Main program entry point
Handles first run check and window initialization
"""
import os
import sys
import signal
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

from .infrastructure.config_manager import ConfigManager
from .infrastructure.memory.vector_store import VectorMemoryStore
from .domain.profile.profile_manager import ProfileManager
from .domain.ai.profile_extractor import ProfileExtractor
from .presentation.floating_window import FloatingWindow
from .presentation.chat_widget import ChatUI
from .presentation.setup_window import SetupWindow
from .presentation.personality_setup_window import PersonalitySetupWindow
from pathlib import Path


class DesktopPetApp:
    """Desktop pet application main class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config_manager = ConfigManager()
        self.window = None
        self.setup_window = None
        self.chat_ui = None
        self.setup_ui = None
        self.ai_provider = None
        # Load conversation history from file
        self.conversation_history = self.config_manager.load_conversation_history()
        
        # Initialize two-tier memory system
        # 1. Vector store for long-term memory (ChromaDB)
        # Uses free local SentenceTransformer model (no API key needed)
        try:
            self.vector_store = VectorMemoryStore(
                persist_directory="./data/chromadb"
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize vector store: {e}")
            self.vector_store = None
        
        # 2. User profile manager
        try:
            self.profile_manager = ProfileManager(
                profile_file=Path("./data/user_profile.json")
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize profile manager: {e}")
            self.profile_manager = None
        
        # Profile extractor will be initialized after AI provider is ready
        self.profile_extractor = None
        
        # Proactive conversation tracking
        self.last_user_message_time = datetime.now()  # Record last user message time
        self.proactive_interval_minutes = 10  # Proactive conversation interval (minutes)
        self.proactive_timer = None  # Proactive conversation timer
        
        # Enable Ctrl+C to quit - use timer to process signals
        signal.signal(signal.SIGINT, self._handle_sigint)
        # Create timer to process signals periodically
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)  # Process events
        self.timer.start(100)  # Check every 100ms
    
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
        # Create large setup window (centered)
        self.setup_window = SetupWindow()
        
        # Create personality setup interface
        self.setup_ui = PersonalitySetupWindow()
        self.setup_ui.personality_saved.connect(self._on_personality_saved)
        self.setup_ui.window_closed.connect(self._on_setup_closed)
        
        # Set content
        self.setup_window.set_content(self.setup_ui)
        
        # Show window (already centered)
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
        
        # Initialize AI provider
        self._init_ai_provider()
        
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
        
        # Load and display conversation history
        self._load_and_display_history()
        
        # Show welcome message only if no history exists
        if not self.conversation_history:
            personality = self.config_manager.load_personality()
            if personality:
                welcome_msg = "Hello! I'm ready to chat with you."
            else:
                welcome_msg = "Hello! I'm your AI companion."
            
            self.chat_ui.add_message(welcome_msg, is_user=False)
            # Add welcome message to conversation history
            self.conversation_history.append({"role": "assistant", "content": welcome_msg})
            # Save after adding welcome message
            self._save_conversation_history()
        
        # Show window
        self.window.show()
        
        # Start proactive conversation timer
        self._start_proactive_timer()
    
    def _init_ai_provider(self):
        """Initialize AI provider based on configuration"""
        try:
            provider_name = self.config_manager.get_ai_provider()
            api_key = self.config_manager.get_api_key(provider_name)
            model = self.config_manager.get_model(provider_name)
            
            print(f"Initializing AI provider: {provider_name}, model: {model}")
            print(f"API key present: {bool(api_key)}")
            
            if not api_key:
                error_msg = f"No API key found for {provider_name}. Please set it in settings or config.json"
                print(f"Warning: {error_msg}")
                self.ai_provider = None
                return
            
            if provider_name == "openai":
                from .domain.ai.providers.openai_provider import OpenAIProvider
                self.ai_provider = OpenAIProvider(api_key=api_key, model=model)
                print("OpenAI provider initialized successfully")
            elif provider_name == "claude":
                from .domain.ai.providers.claude_provider import ClaudeProvider
                self.ai_provider = ClaudeProvider(api_key=api_key, model=model)
                print("Claude provider initialized successfully")
            elif provider_name == "gemini":
                from .domain.ai.providers.gemini_provider import GeminiProvider
                self.ai_provider = GeminiProvider(api_key=api_key, model=model)
                print("Gemini provider initialized successfully")
            else:
                print(f"Warning: Unknown provider {provider_name}")
                self.ai_provider = None
                return
            
            # Initialize profile extractor after AI provider is ready
            if self.ai_provider and self.profile_manager:
                self.profile_extractor = ProfileExtractor(self.ai_provider)
                print("Profile extractor initialized")
                
        except ImportError as e:
            error_msg = f"Failed to import provider module: {e}. Please install required packages."
            print(f"Error: {error_msg}")
            import traceback
            traceback.print_exc()
            self.ai_provider = None
        except Exception as e:
            error_msg = f"Error initializing AI provider: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.ai_provider = None
    
    def _apply_opacity(self, opacity: int):
        """Apply window opacity"""
        if self.window:
            # Convert percentage to 0-1 range
            opacity_value = opacity / 100.0
            self.window.setWindowOpacity(opacity_value)
    
    def _on_settings_changed(self):
        """Handle settings change"""
        config = self.config_manager.load_config()
        opacity = config.get("opacity", 92)
        self._apply_opacity(opacity)
        # Reinitialize AI provider in case API key changed
        self._init_ai_provider()
        # Refresh chat UI to show new avatars
        if self.chat_ui:
            # Re-add last message to refresh avatars
            pass  # Avatars will update on next message
    
    def _on_personality_saved(self, personality: str):
        """Callback after personality settings are saved"""
        # Save personality settings
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
        # If user closes setup without saving, use default
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
        
        # Reset proactive timer (user is actively chatting)
        self._reset_proactive_timer()
        
        # Display user message
        self.chat_ui.add_message(message, is_user=True)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        # Save conversation history after user message
        self._save_conversation_history()
        
        # Show thinking indicator
        self.chat_ui.add_thinking_indicator()
        
        # Generate AI response in background
        from PyQt6.QtCore import QThread, pyqtSignal
        
        # Build system prompt from personality/character config
        # Always use full mode, don't limit personality and RAG
        
        # Get max_tokens from config
        max_tokens = self.config_manager.get_max_tokens()
        
        system_prompt = self._build_system_prompt(
            include_rag=True  # Always include RAG
        )
        
        # Use dynamic history window
        relevant_history = self._get_relevant_history(message)
        
        class AIWorker(QThread):
            response_ready = pyqtSignal(str)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, provider, messages, system_prompt, max_tokens):
                super().__init__()
                self.provider = provider
                self.messages = messages
                self.system_prompt = system_prompt
                self.max_tokens = max_tokens
            
            def run(self):
                try:
                    if self.provider:
                        response = self.provider.generate_response(
                            messages=self.messages,
                            system_prompt=self.system_prompt,
                            max_tokens=self.max_tokens
                        )
                        self.response_ready.emit(response)
                    else:
                        self.error_occurred.emit("AI provider not initialized. Please check your API key in settings.")
                except Exception as e:
                    self.error_occurred.emit(f"Error: {str(e)}")
        
        # Create and start worker thread
        self.ai_worker = AIWorker(
            provider=self.ai_provider,
            messages=relevant_history.copy(),  # Use filtered history
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        self.ai_worker.response_ready.connect(self._on_ai_response)
        self.ai_worker.error_occurred.connect(self._on_ai_error)
        self.ai_worker.start()
    
    def _build_system_prompt(self, include_rag: bool = True) -> str:
        """
        Build system prompt from character configuration, user profile, and relevant memories
        
        Args:
            include_rag: Whether to include RAG
        
        System Prompt Structure:
        1. CRITICAL: Output Example & Performance (highest priority, placed first)
        2. Character Personality
        3. User Profile (from JSON)
        4. Relevant Past Conversations (RAG)
        5. Guidelines (if output_example doesn't exist, use default guidelines)
        """
        parts = []
        character_config = self.config_manager.load_character_config()
        
        # ===== 1. CRITICAL: Output Example & Performance (highest priority, placed first) =====
        # This is the most important part: strictly follow user-set performance to generate messages
        # Placed first to ensure AI sees and follows these requirements first
        has_output_example = False
        if character_config.get("output_example"):
            # Prioritize performance requirements in output_example, mark with CRITICAL
            parts.append(f"⚠️ CRITICAL - Output Example & Performance Requirements (MUST FOLLOW EXACTLY):\n{character_config['output_example']}")
            has_output_example = True
        
        # Notes usually contain important length and style requirements, should be included
        if character_config.get("notes"):
            # If output_example already exists, notes as supplement; otherwise notes as main guidance
            if has_output_example:
                # output_example already contains main requirements, notes as supplementary emphasis
                parts.append(f"⚠️ CRITICAL - Additional Notes (MUST FOLLOW):\n{character_config['notes']}")
            else:
                # When no output_example, notes as main guidance
                parts.append(f"⚠️ CRITICAL - Response Guidelines (MUST FOLLOW):\n{character_config['notes']}")
                has_output_example = True
        
        # ===== 2. Character Personality (full mode, no truncation) =====
        if character_config.get("personality"):
            personality = character_config['personality']
            parts.append(f"Personality: {personality}")
        
        # Other config items always added
        if character_config.get("backstory"):
            parts.append(f"Backstory: {character_config['backstory']}")
        if character_config.get("traits"):
            parts.append(f"Traits: {character_config['traits']}")
        if character_config.get("preferences"):
            parts.append(f"Preferences: {character_config['preferences']}")
        if character_config.get("worldview_background"):
            parts.append(f"Worldview Background: {character_config['worldview_background']}")
        if character_config.get("worldview_setting"):
            parts.append(f"Worldview Setting: {character_config['worldview_setting']}")
        
        # Fallback to simple personality if no detailed config
        if not any("Personality:" in p for p in parts):
            personality = self.config_manager.load_personality()
            if personality:
                parts.append(f"Personality: {personality}")
            else:
                parts.append("You are a friendly and supportive AI companion.")
        
        # ===== 3. User Profile =====
        if self.profile_manager:
            profile = self.profile_manager.get_profile()
            profile_summary = []
            
            if profile.name:
                profile_summary.append(f"User: {profile.name}")
            
            if profile.personality_traits:
                # Only take first 3 traits
                traits = ", ".join(profile.personality_traits[:3])
                profile_summary.append(f"Traits: {traits}")
            
            if profile.goals:
                # Show first 3 goals
                goals = ", ".join(profile.goals[:3])
                profile_summary.append(f"Goals: {goals}")
            
            if profile_summary:
                parts.append(" | ".join(profile_summary))
        
        # ===== 4. Relevant Past Conversations (RAG) - Load on demand, only include high relevance memories =====
        if include_rag and self.vector_store and self.conversation_history:
            last_user_msg = self._get_last_user_message()
            if last_user_msg:
                relevant_convs = self.vector_store.search_relevant_conversations(
                    query=last_user_msg,
                    n_results=2  # Reduced from 3 to 2
                )
                
                # Only include high relevance memories (similarity > 0.7)
                high_relevance_convs = [
                    conv for conv in relevant_convs 
                    if conv.get('relevance_score', 0) > 0.7
                ]
                
                if high_relevance_convs:
                    memory_text = "Relevant memory:\n"
                    conv = high_relevance_convs[0]  # Only take the most relevant one
                    # Limit length of each memory
                    user_msg = conv.get('user_message', '')[:100]
                    ai_resp = conv.get('ai_response', '')[:100]
                    memory_text += f"U: {user_msg}...\nA: {ai_resp}..."
                    parts.append(memory_text)
        
        # ===== 5. Guidelines (only use default guidelines if output_example and notes don't exist) =====
        if not has_output_example:
            # Get max_tokens to adjust response length instruction
            max_tokens = self.config_manager.get_max_tokens()
            
            # Calculate target sentence count based on max_tokens
            # Roughly: 50 tokens = 1 sentence, so adjust accordingly
            if max_tokens <= 100:
                target_sentences = "1-2"
                target_words = "30-50"
            elif max_tokens <= 200:
                target_sentences = "2-3"
                target_words = "50-80"
            else:
                target_sentences = "2-4"
                target_words = "80-120"
            
            parts.append(f"""Guidelines:
- Use the user profile information naturally in conversation
- Reference relevant past conversations when appropriate
- Stay consistent with your personality
- Be proactive and caring
- IMPORTANT: Keep responses concise ({target_sentences} sentences, {target_words} words). Express your complete thought in these few sentences - be brief but complete. Do not start a long response that gets cut off.""")
        
        return "\n\n".join(parts)
    
    def _get_last_user_message(self) -> str:
        """Get user's last message"""
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""
    
    def _get_relevant_history(self, current_message: str) -> list:
        """
        Intelligently select relevant history based on current message
        
        Strategy:
        - Simple greeting/casual chat: only need last 3 messages
        - Ongoing discussion: need last 8-10 messages
        - Complex task: need full 15 messages
        """
        message_lower = current_message.lower()
        word_count = len(current_message.split())
        
        # Determine message type
        is_greeting = any(word in message_lower 
                         for word in ['hello', 'hi', '你好', '嗨', 'hey'])
        is_simple = word_count < 10
        is_question = '?' in current_message or '？' in current_message
        
        # Simple greeting or short message
        if is_greeting or (is_simple and not is_question):
            return self.conversation_history[-3:]  # Only take last 3 messages
        
        # Medium complexity (general questions or discussion)
        elif word_count < 30:
            return self.conversation_history[-8:]  # Medium complexity
        
        # Complex discussion or long message
        else:
            return self.conversation_history[-15:]  # Complex discussion (keep 15 instead of 20)
    
    def _on_ai_response(self, response: str):
        """
        Handle AI response with two-tier memory system
        
        Post-processing steps:
        1. Display message
        2. Add to conversation history
        3. Save to vector database (long-term memory)
        4. Increment conversation count
        5. Update user profile (every 5 conversations)
        6. Limit history to last 20 messages
        7. Save conversation history to JSON
        """
        # 1. Display message
        self.chat_ui.remove_thinking_indicator()
        self.chat_ui.add_message(response, is_user=False)
        
        # 2. Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # 3. Save to vector database (long-term memory)
        if self.vector_store and len(self.conversation_history) >= 2:
            # Get the user message and AI response pair
            user_msg = ""
            for msg in reversed(self.conversation_history[:-1]):  # Exclude the just-added AI response
                if msg.get("role") == "user":
                    user_msg = msg.get("content", "")
                    break
            
            if user_msg:
                try:
                    self.vector_store.add_conversation(user_msg, response)
                    print(f"✓ Saved conversation to vector store")
                except Exception as e:
                    print(f"⚠ Warning: Failed to save to vector store: {e}")
        
        # 4. Increment conversation count
        if self.profile_manager:
            self.profile_manager.increment_conversation_count()
        
        # 5. Update user profile (every 5 conversations)
        if self.profile_manager and self.profile_manager.should_update_profile():
            print(f"📝 Updating user profile (conversation #{self.profile_manager.profile.conversation_count})")
            self._update_user_profile()
        
        # 6. Keep only last 20 messages to avoid context overflow
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        # 7. Save conversation history to JSON
        self._save_conversation_history()
    
    def _on_ai_error(self, error: str):
        """Handle AI error"""
        self.chat_ui.remove_thinking_indicator()
        error_msg = f"Sorry, I encountered an error: {error}"
        self.chat_ui.add_message(error_msg, is_user=False)
        # Add error message to conversation history
        self.conversation_history.append({"role": "assistant", "content": error_msg})
        # Save conversation history after error
        self._save_conversation_history()
    
    def _save_conversation_history(self):
        """Save conversation history to file"""
        try:
            self.config_manager.save_conversation_history(self.conversation_history)
        except Exception as e:
            print(f"Warning: Failed to save conversation history: {e}")
    
    def _load_and_display_history(self):
        """Load conversation history from file and display in chat UI"""
        if not self.conversation_history:
            return
        
        # Display all messages from history
        for msg in self.conversation_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            if content:  # Skip empty messages
                is_user = (role == "user")
                self.chat_ui.add_message(content, is_user=is_user)
        
        # Update last user message time based on history
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "user":
                # Found last user message, but we don't have timestamp
                # Just use current time as approximation
                break
    
    def _start_proactive_timer(self):
        """Start proactive conversation timer"""
        if self.proactive_timer:
            self.proactive_timer.stop()
        
        # Create timer, check every 10 minutes
        self.proactive_timer = QTimer()
        self.proactive_timer.timeout.connect(self._check_and_initiate_proactive_conversation)
        # 10 minutes = 600000 milliseconds
        self.proactive_timer.start(self.proactive_interval_minutes * 60 * 1000)
        print(f"✓ Proactive conversation timer started (interval: {self.proactive_interval_minutes} minutes)")
    
    def _reset_proactive_timer(self):
        """Reset proactive conversation timer (after user sends message)"""
        if self.proactive_timer:
            self.proactive_timer.stop()
            self._start_proactive_timer()
    
    def _check_and_initiate_proactive_conversation(self):
        """Check if proactive conversation should be initiated"""
        if not self.chat_ui or not self.ai_provider:
            return
        
        # Calculate time since last user message
        time_since_last_message = datetime.now() - self.last_user_message_time
        
        # If exceeds set interval, and last message is not AI-initiated
        if time_since_last_message >= timedelta(minutes=self.proactive_interval_minutes):
            # Check if last message was sent by user
            if self.conversation_history:
                last_msg = self.conversation_history[-1]
                # If last message is AI message and is proactively initiated (has marker), skip
                if last_msg.get("role") == "assistant" and last_msg.get("proactive", False):
                    # Already proactively sent message, wait for user reply
                    return
            
            # Initiate proactive conversation
            self._initiate_proactive_conversation()
    
    def _initiate_proactive_conversation(self):
        """Initiate proactive conversation"""
        if not self.ai_provider or not self.chat_ui:
            return
        
        print(f"💬 Initiating proactive conversation after {self.proactive_interval_minutes} minutes of silence")
        
        # Generate proactive conversation message in background thread
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class ProactiveWorker(QThread):
            message_ready = pyqtSignal(str)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, provider, conversation_history, system_prompt, max_tokens):
                super().__init__()
                self.provider = provider
                self.conversation_history = conversation_history
                self.system_prompt = system_prompt
                self.max_tokens = max_tokens
            
            def run(self):
                try:
                    if self.provider:
                        # Build proactive conversation prompt
                        proactive_prompt = """Generate a brief, natural proactive message to check in with the user. 
Keep it warm, caring, and not intrusive. It should feel like a friend checking in, not a notification.
Keep it short (1-2 sentences). Express your complete thought concisely - don't cut off mid-sentence."""
                        
                        # Use simplified context (only include last 3 messages)
                        recent_context = self.conversation_history[-3:] if len(self.conversation_history) > 3 else self.conversation_history
                        
                        # Build messages
                        messages = recent_context.copy()
                        messages.append({
                            "role": "user",
                            "content": "[Generate a proactive check-in message based on our conversation context and your personality]"
                        })
                        
                        # Enhanced system prompt
                        enhanced_system_prompt = f"{self.system_prompt}\n\n{proactive_prompt}"
                        
                        response = self.provider.generate_response(
                            messages=messages,
                            system_prompt=enhanced_system_prompt,
                            max_tokens=self.max_tokens
                        )
                        self.message_ready.emit(response)
                    else:
                        self.error_occurred.emit("AI provider not initialized")
                except Exception as e:
                    self.error_occurred.emit(f"Error: {str(e)}")
        
        # Build system prompt
        system_prompt = self._build_system_prompt(include_rag=True)
        
        # Get max_tokens configuration
        max_tokens = self.config_manager.get_max_tokens()
        
        # Create and start worker thread
        self.proactive_worker = ProactiveWorker(
            provider=self.ai_provider,
            conversation_history=self.conversation_history.copy(),
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        self.proactive_worker.message_ready.connect(self._on_proactive_message)
        self.proactive_worker.error_occurred.connect(self._on_proactive_error)
        self.proactive_worker.start()
    
    def _on_proactive_message(self, message: str):
        """Handle proactive conversation message"""
        # Display message
        self.chat_ui.add_message(message, is_user=False)
        
        # Add to conversation history, mark as proactively initiated
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "proactive": True  # Mark as proactively initiated
        })
        
        # Save conversation history
        self._save_conversation_history()
        
        # Reset timer
        self._reset_proactive_timer()
        
        print(f"✓ Proactive message sent: {message[:50]}...")
    
    def _on_proactive_error(self, error: str):
        """Handle proactive conversation error"""
        print(f"✗ Proactive conversation failed: {error}")
        # Reset timer even on failure to avoid repeated attempts
        self._reset_proactive_timer()
    
    def _update_user_profile(self):
        """
        Use AI to update user profile
        
        This runs in a background thread to avoid blocking the UI
        """
        if not self.profile_extractor or not self.profile_manager:
            return
        
        # Get recent messages for analysis (last 10 messages)
        recent_messages = self.conversation_history[-10:] if len(self.conversation_history) >= 10 else self.conversation_history
        
        # Run in background thread
        from PyQt6.QtCore import QThread
        
        class ProfileUpdateWorker(QThread):
            def __init__(self, extractor, profile_manager, messages):
                super().__init__()
                self.extractor = extractor
                self.profile_manager = profile_manager
                self.messages = messages
            
            def run(self):
                try:
                    print("🔍 Extracting user information from conversation...")
                    extracted_data = self.extractor.extract_user_info(self.messages)
                    self.profile_manager.update_profile_from_ai(extracted_data)
                    print(f"✓ Profile update completed")
                except Exception as e:
                    print(f"✗ Profile update failed: {e}")
        
        worker = ProfileUpdateWorker(self.profile_extractor, self.profile_manager, recent_messages)
        worker.start()


def main():
    """Main function"""
    app = DesktopPetApp()
    app.run()


if __name__ == "__main__":
    main()

