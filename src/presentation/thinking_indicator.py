"""
Thinking indicator with animated dots
Provides emotional, non-intrusive loading state
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from .ui_styles_premium import COLORS, THINKING_TEXT


class ThinkingIndicator(QWidget):
    """Animated thinking indicator with emotional messages"""
    
    MESSAGES = [
        "Thinking...",
        "Let me think...",
        "Just a moment...",
        "Processing...",
        "Let me organize my thoughts...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_message_index = 0
        self.dot_count = 0
        self._setup_ui()
        self._start_animation()
    
    def _setup_ui(self):
        """Set up UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Message label
        self.message_label = QLabel(self.MESSAGES[0])
        self.message_label.setStyleSheet(THINKING_TEXT)
        layout.addWidget(self.message_label)
        
        # Animated dots
        self.dots_label = QLabel("")
        self.dots_label.setStyleSheet(THINKING_TEXT)
        layout.addWidget(self.dots_label)
        
        layout.addStretch()
    
    def _start_animation(self):
        """Start dot animation"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_dots)
        self.timer.start(500)  # Update every 500ms
        
        # Change message every 3 seconds
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self._update_message)
        self.message_timer.start(3000)
    
    def _update_dots(self):
        """Update animated dots"""
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.dots_label.setText(dots)
    
    def _update_message(self):
        """Update thinking message"""
        self.current_message_index = (self.current_message_index + 1) % len(self.MESSAGES)
        self.message_label.setText(self.MESSAGES[self.current_message_index])
    
    def stop(self):
        """Stop animation"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'message_timer'):
            self.message_timer.stop()

