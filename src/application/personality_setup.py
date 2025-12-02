"""
Personality setup interface
Displayed on first launch, used to configure AI personality
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..presentation.ui_styles_legacy import (
    TITLE_STYLE, SUBTITLE_STYLE, LABEL_STYLE,
    INPUT_STYLE, SCROLL_AREA_STYLE,
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    COLORS
)


class PersonalitySetup(QWidget):
    """Personality setup interface"""
    
    # Signal: triggered when personality setup is complete
    personality_saved = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Welcome to AI Desktop Pet")
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)
        
        # Description text
        description = QLabel(
            "Please describe the personality traits you want for your AI companion.\n"
            "For example: friendly, supportive, humorous, calm, etc."
        )
        description.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(description)
        
        # Example prompts area
        examples_label = QLabel("Example prompts:")
        examples_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(examples_label)
        
        examples_area = self._create_examples_area()
        layout.addWidget(examples_area)
        
        # Input field
        input_label = QLabel("Personality description:")
        input_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(input_label)
        
        self.personality_input = QTextEdit()
        self.personality_input.setPlaceholderText(
            "For example: You are a friendly and supportive AI companion. You are always positive and optimistic, "
            "providing encouragement and advice when users need it. You like to communicate in a warm and relaxed tone."
        )
        self.personality_input.setMinimumHeight(120)
        self.personality_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.personality_input, 1)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Use default personality button
        default_btn = QPushButton("Use Default")
        default_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        default_btn.clicked.connect(self._use_default)
        button_layout.addWidget(default_btn)
        
        # Save button
        save_btn = QPushButton("Save and Start")
        save_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        save_btn.clicked.connect(self._save_personality)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_examples_area(self) -> QScrollArea:
        """Create example prompts area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(110)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLL_AREA_STYLE)
        
        examples_widget = QWidget()
        examples_layout = QVBoxLayout(examples_widget)
        examples_layout.setContentsMargins(10, 10, 10, 10)
        examples_layout.setSpacing(5)
        
        examples = [
            "Friendly and supportive",
            "Witty and sarcastic",
            "Calm and philosophical",
            "Energetic and enthusiastic",
            "Gentle and caring"
        ]
        
        for example in examples:
            label = QLabel(f"• {example}")
            label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {COLORS["text_secondary"]};
                    padding: 4px 2px;
                }}
            """)
            examples_layout.addWidget(label)
        
        scroll.setWidget(examples_widget)
        return scroll
    
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
    
    def _get_default_personality(self) -> str:
        """Get default personality description"""
        return (
            "You are a friendly and supportive AI companion. You are always positive and optimistic, "
            "providing encouragement and advice when users need it. You like to communicate in a warm and relaxed tone, "
            "and you will remember users' personal information and preferences to provide more personalized companionship."
        )

