"""
Settings window for AI Desktop Pet
Allows users to customize avatar, appearance, and other settings
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea, QSlider, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
# Compatible with relative and absolute imports
try:
    from .ui_styles_refined import COLORS, SEND_BUTTON
    from ..infrastructure.config_manager import ConfigManager
except ImportError:
    from ui_styles_refined import COLORS, SEND_BUTTON
    from infrastructure.config_manager import ConfigManager


class SettingsWindow(QWidget):
    """Settings window for customization"""
    
    settings_changed = pyqtSignal()  # Emitted when settings are saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.user_avatar_path = None
        self.ai_avatar_path = None
        self.drag_position = None
        self.character_fields = {}
        self.openai_radio = None
        self.claude_radio = None
        self.gemini_radio = None
        self.openai_key_input = None
        self.claude_key_input = None
        self.gemini_key_input = None
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with title and close button
        header = self._create_header()
        layout.addWidget(header)
        
        # Scrollable main content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: white;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS["border_medium"]};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS["primary_focus"]};
            }}
        """)
        
        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)  # More padding for spacious feel
        content_layout.setSpacing(24)  # More spacing between sections
        
        # Avatar settings section
        avatar_section = self._create_avatar_section()
        content_layout.addWidget(avatar_section)
        
        # API settings section
        api_section = self._create_api_section()
        content_layout.addWidget(api_section)
        
        # Character/Personality settings section
        character_section = self._create_character_section()
        content_layout.addWidget(character_section)
        
        # Appearance settings section
        appearance_section = self._create_appearance_section()
        content_layout.addWidget(appearance_section)
        
        content_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["bg_secondary"]};
                color: {COLORS["text_primary"]};
                border: 1.5px solid {COLORS["border_medium"]};
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS["bg_input"]};
                border-color: {COLORS["primary_focus"]};
            }}
        """)
        cancel_btn.clicked.connect(self._close_window)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["primary_medium"]};
                color: {COLORS["text_primary"]};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS["primary_hover"]};
            }}
        """)
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        content_layout.addLayout(button_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
    
    def _create_header(self) -> QWidget:
        """Create header with title and close button"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS["primary"]}, 
                    stop:1 rgba(236, 72, 153, 1));
                border-top-left-radius: 28px;
                border-top-right-radius: 28px;
            }}
        """)
        # Make header draggable
        header.mousePressEvent = self._header_mouse_press
        header.mouseMoveEvent = self._header_mouse_move
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(12)
        
        # Title with background pill
        title_container = QWidget()
        title_container.setStyleSheet(f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                padding: 8px 16px;
            }}
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: white;
                letter-spacing: 0px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
                background: transparent;
            }}
        """)
        title_layout.addWidget(title)
        layout.addWidget(title_container)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        close_btn.clicked.connect(self._close_window)
        layout.addWidget(close_btn)
        
        return header
    
    def _header_mouse_press(self, event):
        """Handle mouse press on header for dragging"""
        from PyQt6.QtCore import QPoint
        if event.button() == Qt.MouseButton.LeftButton:
            parent_window = self.window()
            if parent_window:
                self.drag_position = event.globalPosition().toPoint() - parent_window.frameGeometry().topLeft()
                event.accept()
    
    def _header_mouse_move(self, event):
        """Handle mouse move on header for dragging"""
        from PyQt6.QtCore import QPoint
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position') and self.drag_position is not None:
            parent_window = self.window()
            if parent_window:
                parent_window.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
    
    def _close_window(self):
        """Close settings window"""
        parent_window = self.window()
        if parent_window:
            parent_window.close()
    
    def _create_avatar_section(self) -> QWidget:
        """Create avatar settings section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Section title
        title = QLabel("Avatars")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        layout.addWidget(title)
        
        # User avatar
        user_layout = QHBoxLayout()
        user_layout.setSpacing(16)
        
        user_label = QLabel("Your Avatar:")
        user_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {COLORS["text_secondary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        user_layout.addWidget(user_label)
        
        self.user_avatar_btn = QPushButton("👤")
        self.user_avatar_btn.setFixedSize(64, 64)  # Larger avatar button
        self.user_avatar_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["bg_secondary"]};
                border: 2px solid {COLORS["border_light"]};
                border-radius: 32px;
                font-size: 32px;
            }}
            QPushButton:hover {{
                border-color: {COLORS["primary_focus"]};
                background: {COLORS["bg_input"]};
            }}
        """)
        self.user_avatar_btn.clicked.connect(lambda: self._select_avatar("user"))
        user_layout.addWidget(self.user_avatar_btn)
        
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        # AI avatar
        ai_layout = QHBoxLayout()
        ai_layout.setSpacing(16)
        
        ai_label = QLabel("AI Avatar:")
        ai_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {COLORS["text_secondary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        ai_layout.addWidget(ai_label)
        
        self.ai_avatar_btn = QPushButton("✨")
        self.ai_avatar_btn.setFixedSize(64, 64)  # Larger avatar button
        self.ai_avatar_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["bg_secondary"]};
                border: 2px solid {COLORS["border_light"]};
                border-radius: 32px;
                font-size: 32px;
            }}
            QPushButton:hover {{
                border-color: {COLORS["primary_focus"]};
                background: {COLORS["bg_input"]};
            }}
        """)
        self.ai_avatar_btn.clicked.connect(lambda: self._select_avatar("ai"))
        ai_layout.addWidget(self.ai_avatar_btn)
        
        ai_layout.addStretch()
        layout.addLayout(ai_layout)
        
        return section
    
    def _create_api_section(self) -> QWidget:
        """Create API settings section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Section title
        title = QLabel("API Settings")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        layout.addWidget(title)
        
        # AI Provider selection
        provider_layout = QVBoxLayout()
        provider_layout.setSpacing(8)
        
        provider_label = QLabel("AI Provider:")
        provider_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        provider_layout.addWidget(provider_label)
        
        provider_buttons_layout = QHBoxLayout()
        provider_buttons_layout.setSpacing(8)
        
        button_style = f"""
            QPushButton {{
                background: {COLORS["bg_secondary"]};
                color: {COLORS["text_primary"]};
                border: 2px solid {COLORS["border_light"]};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:checked {{
                background: {COLORS["primary_medium"]};
                border-color: {COLORS["primary"]};
                color: white;
            }}
            QPushButton:hover {{
                border-color: {COLORS["primary_focus"]};
            }}
        """
        
        self.openai_radio = QPushButton("OpenAI")
        self.openai_radio.setCheckable(True)
        self.openai_radio.setStyleSheet(button_style)
        self.openai_radio.clicked.connect(lambda: self._on_provider_changed("openai"))
        provider_buttons_layout.addWidget(self.openai_radio)
        
        self.claude_radio = QPushButton("Claude")
        self.claude_radio.setCheckable(True)
        self.claude_radio.setStyleSheet(button_style)
        self.claude_radio.clicked.connect(lambda: self._on_provider_changed("claude"))
        provider_buttons_layout.addWidget(self.claude_radio)
        
        self.gemini_radio = QPushButton("Gemini")
        self.gemini_radio.setCheckable(True)
        self.gemini_radio.setStyleSheet(button_style)
        self.gemini_radio.clicked.connect(lambda: self._on_provider_changed("gemini"))
        provider_buttons_layout.addWidget(self.gemini_radio)
        
        provider_buttons_layout.addStretch()
        provider_layout.addLayout(provider_buttons_layout)
        layout.addLayout(provider_layout)
        
        # OpenAI API Key
        openai_layout = QVBoxLayout()
        openai_layout.setSpacing(6)
        
        openai_label = QLabel("OpenAI API Key:")
        openai_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        openai_layout.addWidget(openai_label)
        
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setPlaceholderText("sk-...")
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_input.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1px solid {COLORS["border_light"]};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["primary_focus"]};
            }}
        """)
        openai_layout.addWidget(self.openai_key_input)
        layout.addLayout(openai_layout)
        
        # Claude API Key
        claude_layout = QVBoxLayout()
        claude_layout.setSpacing(6)
        
        claude_label = QLabel("Claude API Key:")
        claude_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        claude_layout.addWidget(claude_label)
        
        self.claude_key_input = QLineEdit()
        self.claude_key_input.setPlaceholderText("sk-ant-...")
        self.claude_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key_input.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1px solid {COLORS["border_light"]};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["primary_focus"]};
            }}
        """)
        claude_layout.addWidget(self.claude_key_input)
        layout.addLayout(claude_layout)
        
        # Gemini API Key
        gemini_layout = QVBoxLayout()
        gemini_layout.setSpacing(6)
        
        gemini_label = QLabel("Gemini API Key:")
        gemini_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        gemini_layout.addWidget(gemini_label)
        
        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setPlaceholderText("AIza...")
        self.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key_input.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1px solid {COLORS["border_light"]};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["primary_focus"]};
            }}
        """)
        gemini_layout.addWidget(self.gemini_key_input)
        layout.addLayout(gemini_layout)
        
        return section
    
    def _on_provider_changed(self, provider: str):
        """Handle provider selection change"""
        self.openai_radio.setChecked(provider == "openai")
        self.claude_radio.setChecked(provider == "claude")
        self.gemini_radio.setChecked(provider == "gemini")
    
    def _create_character_section(self) -> QWidget:
        """Create character/personality settings section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Section title
        title = QLabel("Character Settings")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        layout.addWidget(title)
        
        # Define all character fields
        self.character_fields = {}
        field_definitions = [
            ("personality", "Personality", "Describe the character's basic personality and identity"),
            ("backstory", "Backstory", "Describe the character's growth background and experiences"),
            ("traits", "Traits", "Describe the character's personality traits"),
            ("preferences", "Preferences", "Describe the character's likes and preferences"),
            ("output_example", "Output Example", "Provide examples of the desired output style"),
            ("user_profile", "User Profile", "Describe the user's basic information and characteristics"),
            ("worldview_background", "Worldview Background", "Describe the basic background of the worldview"),
            ("worldview_setting", "Worldview Setting", "Describe the specific settings of the worldview"),
            ("notes", "Notes", "Other important notes and considerations")
        ]
        
        for field_key, field_label, field_hint in field_definitions:
            # Field label
            field_label_widget = QLabel(f"{field_label}:")
            field_label_widget.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    font-weight: 500;
                    color: {COLORS["text_primary"]};
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
                }}
            """)
            layout.addWidget(field_label_widget)
            
            # Field input
            field_input = QTextEdit()
            field_input.setPlaceholderText(field_hint)
            field_input.setMaximumHeight(100)
            field_input.setStyleSheet(f"""
                QTextEdit {{
                    background: white;
                    border: 1px solid {COLORS["border_light"]};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                    color: {COLORS["text_primary"]};
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
                }}
                QTextEdit:focus {{
                    border-color: {COLORS["primary_focus"]};
                }}
            """)
            self.character_fields[field_key] = field_input
            layout.addWidget(field_input)
        
        return section
    
    def _create_appearance_section(self) -> QWidget:
        """Create appearance settings section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Section title
        title = QLabel("Appearance")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {COLORS["text_primary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        layout.addWidget(title)
        
        # Window opacity
        opacity_layout = QVBoxLayout()  # Vertical layout for better spacing
        opacity_layout.setSpacing(8)
        
        opacity_label = QLabel("Window Opacity:")
        opacity_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {COLORS["text_secondary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        opacity_layout.addWidget(opacity_label)
        
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(12)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(70)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(92)
        self.opacity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS["border_light"]};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS["primary"]};
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -7px 0;
            }}
        """)
        slider_layout.addWidget(self.opacity_slider, 1)
        
        self.opacity_value = QLabel("92%")
        self.opacity_value.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {COLORS["text_secondary"]};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
                min-width: 50px;
            }}
        """)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_value.setText(f"{v}%")
        )
        slider_layout.addWidget(self.opacity_value)
        
        opacity_layout.addLayout(slider_layout)
        layout.addLayout(opacity_layout)
        
        return section
    
    def _select_avatar(self, avatar_type: str):
        """Open file dialog to select avatar image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {avatar_type.upper()} Avatar",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to 48x48
                scaled = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                
                if avatar_type == "user":
                    self.user_avatar_btn.setIcon(QIcon(scaled))
                    self.user_avatar_btn.setText("")
                    self.user_avatar_path = file_path
                else:
                    self.ai_avatar_btn.setIcon(QIcon(scaled))
                    self.ai_avatar_btn.setText("")
                    self.ai_avatar_path = file_path
    
    def _load_settings(self):
        """Load current settings"""
        config = self.config_manager.load_config()
        
        # Load avatars
        if "user_avatar" in config and config["user_avatar"]:
            try:
                pixmap = QPixmap(config["user_avatar"])
                if not pixmap.isNull():
                    scaled = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                    self.user_avatar_btn.setIcon(QIcon(scaled))
                    self.user_avatar_btn.setText("")
                    self.user_avatar_path = config["user_avatar"]
            except:
                pass
        
        if "ai_avatar" in config and config["ai_avatar"]:
            try:
                pixmap = QPixmap(config["ai_avatar"])
                if not pixmap.isNull():
                    scaled = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                    self.ai_avatar_btn.setIcon(QIcon(scaled))
                    self.ai_avatar_btn.setText("")
                    self.ai_avatar_path = config["ai_avatar"]
            except:
                pass
        
        # Load opacity
        if "opacity" in config:
            self.opacity_slider.setValue(config["opacity"])
        
        # Load API settings
        ai_provider = self.config_manager.get_ai_provider()
        self._on_provider_changed(ai_provider)
        
        # Load API keys (masked for display)
        openai_key = self.config_manager.get_api_key("openai")
        if openai_key:
            self.openai_key_input.setText(openai_key)  # Display will be masked by password mode
        
        claude_key = self.config_manager.get_api_key("claude")
        if claude_key:
            self.claude_key_input.setText(claude_key)
        
        gemini_key = self.config_manager.get_api_key("gemini")
        if gemini_key:
            self.gemini_key_input.setText(gemini_key)
        
        # Load character settings
        character_config = self.config_manager.load_character_config()
        for field_key, field_input in self.character_fields.items():
            if field_key in character_config:
                field_input.setPlainText(character_config[field_key])
    
    def _save_settings(self):
        """Save settings"""
        config = self.config_manager.load_config()
        
        # Save avatars
        if hasattr(self, 'user_avatar_path'):
            config["user_avatar"] = self.user_avatar_path
        if hasattr(self, 'ai_avatar_path'):
            config["ai_avatar"] = self.ai_avatar_path
        
        # Save opacity
        config["opacity"] = self.opacity_slider.value()
        
        # Save API settings
        if self.openai_radio.isChecked():
            self.config_manager.set_ai_provider("openai")
        elif self.claude_radio.isChecked():
            self.config_manager.set_ai_provider("claude")
        elif self.gemini_radio.isChecked():
            self.config_manager.set_ai_provider("gemini")
        
        # Save API keys
        openai_key = self.openai_key_input.text().strip()
        if openai_key:
            self.config_manager.save_api_key("openai", openai_key)
        
        claude_key = self.claude_key_input.text().strip()
        if claude_key:
            self.config_manager.save_api_key("claude", claude_key)
        
        gemini_key = self.gemini_key_input.text().strip()
        if gemini_key:
            self.config_manager.save_api_key("gemini", gemini_key)
        
        self.config_manager.save_config(config)
        
        # Save character settings
        character_config = {}
        for field_key, field_input in self.character_fields.items():
            character_config[field_key] = field_input.toPlainText().strip()
        self.config_manager.save_character_config(character_config)
        
        self.settings_changed.emit()
        self._close_window()

