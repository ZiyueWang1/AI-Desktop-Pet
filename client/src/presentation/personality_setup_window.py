"""
Personality setup window with header and close button
Complete setup interface in a large centered window
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
# Compatible with relative and absolute imports
try:
    from .ui_styles_premium import (
        TITLE_LARGE, BODY_TEXT, LABEL_TEXT,
        INPUT_FIELD, SCROLL_AREA,
        PRIMARY_BUTTON, SECONDARY_BUTTON,
        EXAMPLE_CARD, COLORS, CAPTION_TEXT
    )
except ImportError:
    from ui_styles_premium import (
        TITLE_LARGE, BODY_TEXT, LABEL_TEXT,
        INPUT_FIELD, SCROLL_AREA,
        PRIMARY_BUTTON, SECONDARY_BUTTON,
        EXAMPLE_CARD, COLORS, CAPTION_TEXT
    )


class PersonalitySetupWindow(QWidget):
    """Complete personality setup window with header"""
    
    # Signal: triggered when personality setup is complete
    personality_saved = pyqtSignal(str)
    window_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header bar
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content
        content = self._create_content()
        layout.addWidget(content, 1)
    
    def _create_header(self) -> QWidget:
        """Create header bar with title and close button"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS["primary_gradient_start"]}, 
                    stop:1 {COLORS["primary_gradient_end"]});
                border-top-left-radius: 28px;
                border-top-right-radius: 28px;
            }}
        """)
        # Make header draggable
        header.mousePressEvent = self._header_mouse_press
        header.mouseMoveEvent = self._header_mouse_move
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 10, 0)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Welcome to AI Desktop Pet")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 700;
                color: white;
                letter-spacing: -0.5px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        close_btn.clicked.connect(self._close_window)
        layout.addWidget(close_btn)
        
        return header
    
    def _create_content(self) -> QWidget:
        """Create main content area"""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Description text
        description = QLabel(
            "Please describe the personality traits you want for your AI companion.\n"
            "For example: friendly, supportive, humorous, calm, etc."
        )
        description.setStyleSheet(BODY_TEXT)
        layout.addWidget(description)
        
        # Example prompts area
        examples_label = QLabel("Example prompts:")
        examples_label.setStyleSheet(LABEL_TEXT)
        layout.addWidget(examples_label)
        
        examples_area = self._create_examples_area()
        layout.addWidget(examples_area)
        
        # Input field with character counter
        input_label = QLabel("Personality description:")
        input_label.setStyleSheet(LABEL_TEXT)
        layout.addWidget(input_label)
        
        self.personality_input = QTextEdit()
        self.personality_input.setPlaceholderText(
            "Describe your AI companion's personality...\n\n"
            "For example: You are a friendly and supportive AI companion. You are always positive and optimistic, "
            "providing encouragement and advice when users need it. You like to communicate in a warm and relaxed tone."
        )
        self.personality_input.setMinimumHeight(150)
        self.personality_input.setStyleSheet(INPUT_FIELD)
        self.personality_input.textChanged.connect(self._update_char_count)
        layout.addWidget(self.personality_input, 1)
        
        # Character counter and hint
        hint_layout = QHBoxLayout()
        hint_layout.addStretch()
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setStyleSheet(CAPTION_TEXT)
        hint_layout.addWidget(self.char_count_label)
        layout.addLayout(hint_layout)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Use default personality button
        default_btn = QPushButton("Use Default")
        default_btn.setStyleSheet(SECONDARY_BUTTON)
        default_btn.clicked.connect(self._use_default)
        button_layout.addWidget(default_btn)
        
        # Save button
        save_btn = QPushButton("Save and Start")
        save_btn.setStyleSheet(PRIMARY_BUTTON)
        save_btn.clicked.connect(self._save_personality)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        return content
    
    def _create_examples_area(self) -> QScrollArea:
        """Create clickable example cards area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(140)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLL_AREA)
        
        examples_widget = QWidget()
        examples_layout = QVBoxLayout(examples_widget)
        examples_layout.setContentsMargins(12, 12, 12, 12)
        examples_layout.setSpacing(8)
        
        examples = [
            ("Friendly and supportive", "You are warm, encouraging, and always there to help."),
            ("Witty and sarcastic", "You have a sharp sense of humor and love playful banter."),
            ("Calm and philosophical", "You are thoughtful, reflective, and enjoy deep conversations."),
            ("Energetic and enthusiastic", "You are upbeat, motivating, and full of positive energy."),
            ("Gentle and caring", "You are kind, empathetic, and provide emotional support.")
        ]
        
        for title, desc in examples:
            card = QPushButton(f"✨ {title}\n{desc}")
            card.setStyleSheet(EXAMPLE_CARD)
            # Connect to fill input
            card.clicked.connect(lambda checked, t=title, d=desc: self._fill_example(t, d))
            examples_layout.addWidget(card)
        
        scroll.setWidget(examples_widget)
        return scroll
    
    def _fill_example(self, title: str, desc: str):
        """Fill input with example"""
        text = f"You are {title.lower()}. {desc}"
        self.personality_input.setPlainText(text)
        self._update_char_count()
    
    def _update_char_count(self):
        """Update character count"""
        count = len(self.personality_input.toPlainText())
        color = COLORS["text_secondary"] if 50 <= count <= 500 else COLORS["accent"]
        self.char_count_label.setText(f"{count} characters")
        self.char_count_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {color};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
            }}
        """)
    
    def _save_personality(self):
        """Save personality settings"""
        personality = self.personality_input.toPlainText().strip()
        if not personality:
            personality = self._get_default_personality()
        self.personality_saved.emit(personality)
    
    def _use_default(self):
        """Use default personality"""
        default = self._get_default_personality()
        self.personality_saved.emit(default)
    
    def _close_window(self):
        """Close window"""
        self.window_closed.emit()
    
    def _get_default_personality(self) -> str:
        """Get default personality description"""
        return (
            "You are a friendly and supportive AI companion. You are always positive and optimistic, "
            "providing encouragement and advice when users need it. You like to communicate in a warm and relaxed tone, "
            "and you will remember users' personal information and preferences to provide more personalized companionship."
        )
    
    def _header_mouse_press(self, event):
        """Handle mouse press on header for dragging"""
        from PyQt6.QtCore import QPoint
        if event.button() == Qt.MouseButton.LeftButton:
            # Get parent window (SetupWindow)
            parent_window = self.window()
            if parent_window:
                self.drag_position = event.globalPosition().toPoint() - parent_window.frameGeometry().topLeft()
                event.accept()
    
    def _header_mouse_move(self, event):
        """Handle mouse move on header for dragging"""
        from PyQt6.QtCore import QPoint
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            parent_window = self.window()
            if parent_window:
                parent_window.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
    
    def mousePressEvent(self, event):
        """Handle mouse press on content area for dragging"""
        from PyQt6.QtCore import QPoint
        # Only allow dragging on empty areas (not on interactive elements)
        widget = self.childAt(event.position().toPoint())
        if widget and isinstance(widget, (QPushButton, QTextEdit, QScrollArea)):
            return super().mousePressEvent(event)
        
        if event.button() == Qt.MouseButton.LeftButton:
            parent_window = self.window()
            if parent_window:
                self.drag_position = event.globalPosition().toPoint() - parent_window.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move on content area for dragging"""
        from PyQt6.QtCore import QPoint
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            parent_window = self.window()
            if parent_window:
                parent_window.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

