"""
Chat interface component
Implements message display area and input field
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QScrollArea, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor
from .ui_styles_refined import (
    INPUT_FIELD, INPUT_CONTAINER, SCROLL_AREA,
    SEND_BUTTON,
    USER_MESSAGE, AI_MESSAGE, MESSAGE_TEXT,
    STATUS_INDICATOR, STATUS_TEXT,
    COLORS
)
from ..infrastructure.config_manager import ConfigManager
from .thinking_indicator import ThinkingIndicator


class ChatUI(QWidget):
    """Chat interface component"""
    
    # Signal: triggered when user sends a message
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None
        self.config_manager = ConfigManager()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)  # Reduced top margin
        layout.setSpacing(10)
        
        # Message display area
        self.message_area = self._create_message_area()
        layout.addWidget(self.message_area, 1)
        
        # Input area
        input_area = self._create_input_area()
        layout.addWidget(input_area)
    
    def _create_message_area(self) -> QScrollArea:
        """Create message display area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLL_AREA)
        
        # Message container
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(16, 16, 16, 16)
        self.message_layout.setSpacing(8)  # Optimized spacing for readability
        self.message_layout.addStretch()
        
        # Add status indicator at the top
        self._add_status_indicator()
        
        scroll.setWidget(self.message_container)
        return scroll
    
    def _create_input_area(self) -> QWidget:
        """Create unified input area with container"""
        # Outer container with unified design
        outer_container = QWidget()
        outer_container.setStyleSheet(INPUT_CONTAINER)
        layout = QHBoxLayout(outer_container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Text input field - no border, transparent
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(72)
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setStyleSheet(INPUT_FIELD)
        
        # Bind Enter key event
        self.input_field.keyPressEvent = self._handle_key_press
        
        layout.addWidget(self.input_field, 1)
        
        # Send button - minimal, no gradient
        send_btn = QPushButton("→")
        send_btn.setFixedSize(44, 44)
        send_btn.setStyleSheet(SEND_BUTTON)
        send_btn.clicked.connect(self._send_message)
        layout.addWidget(send_btn)
        
        return outer_container
    
    def _handle_key_press(self, event):
        """Handle keyboard key press events"""
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            # Enter key (no Shift): send message
            self._send_message()
        elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            # Shift+Enter: new line
            QTextEdit.keyPressEvent(self.input_field, event)
        else:
            # Other keys: normal processing
            QTextEdit.keyPressEvent(self.input_field, event)
    
    def _send_message(self):
        """Send message"""
        text = self.input_field.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.input_field.clear()
            # Reset cursor position
            self.input_field.setFocus()
    
    def add_message(self, text: str, is_user: bool = True):
        """
        Add message to display area
        
        Args:
            text: Message text
            is_user: True for user message, False for AI message
        """
        message_widget = self._create_message_bubble(text, is_user)
        
        # Insert message before stretch
        self.message_layout.insertWidget(
            self.message_layout.count() - 1,
            message_widget
        )
        
        # Scroll to bottom
        scroll = self.message_area
        scroll.verticalScrollBar().setValue(
            scroll.verticalScrollBar().maximum()
        )
    
    def _create_message_bubble(self, text: str, is_user: bool) -> QWidget:
        """Create message bubble with companion-like design"""
        # Outer container for avatar + bubble
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Load avatars from config
        config = self.config_manager.load_config()
        
        # Create message bubble widget
        bubble = QWidget()
        bubble_layout = QHBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(0)
        
        if is_user:
            # User message: right-aligned
            # Add stretch to push content to right
            layout.addStretch()
            
            # Create bubble with text
            bubble.setStyleSheet(USER_MESSAGE)
            label = QLabel(text)
            label.setWordWrap(True)
            label.setStyleSheet(MESSAGE_TEXT)
            bubble_layout.addWidget(label)
            
            # Add bubble to container
            layout.addWidget(bubble)
            
            # User avatar (outside bubble, on the right)
            avatar = self._create_avatar(config.get("user_avatar"), "👤")
            layout.addWidget(avatar)
        else:
            # AI message: left-aligned
            # AI avatar (outside bubble, on the left)
            avatar = self._create_avatar(config.get("ai_avatar"), "✨")
            layout.addWidget(avatar)
            
            # Create bubble with text
            bubble.setStyleSheet(AI_MESSAGE)
            label = QLabel(text)
            label.setWordWrap(True)
            label.setStyleSheet(MESSAGE_TEXT)
            bubble_layout.addWidget(label)
            
            # Add bubble to container
            layout.addWidget(bubble)
            
            # Add stretch to push content to left
            layout.addStretch()
        
        return container
    
    def _create_avatar(self, avatar_path: str = None, default_emoji: str = "👤") -> QLabel:
        """Create avatar label"""
        from PyQt6.QtGui import QPixmap, QIcon
        from PyQt6.QtCore import QSize
        
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        
        if avatar_path:
            try:
                pixmap = QPixmap(avatar_path)
                if not pixmap.isNull():
                    # Create circular mask for avatar
                    scaled = pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                    avatar.setPixmap(scaled)
                    avatar.setStyleSheet(f"""
                        QLabel {{
                            background: transparent;
                            border: 2px solid {COLORS["border_light"]};
                            border-radius: 18px;
                            padding: 0px;
                        }}
                    """)
                    return avatar
            except:
                pass
        
        # Use emoji as fallback
        avatar.setText(default_emoji)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: {COLORS["bg_secondary"]};
                border: 2px solid {COLORS["border_light"]};
                border-radius: 18px;
                font-size: 20px;
                padding: 0px;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return avatar
    
    def add_thinking_indicator(self):
        """Add animated thinking indicator"""
        thinking_widget = ThinkingIndicator()
        
        # Insert before stretch
        self.message_layout.insertWidget(
            self.message_layout.count() - 1,
            thinking_widget
        )
        
        # Store reference for removal
        self.current_thinking = thinking_widget
        
        # Scroll to bottom
        scroll = self.message_area
        scroll.verticalScrollBar().setValue(
            scroll.verticalScrollBar().maximum()
        )
    
    def remove_thinking_indicator(self):
        """Remove thinking indicator"""
        if hasattr(self, 'current_thinking') and self.current_thinking:
            self.current_thinking.stop()
            self.message_layout.removeWidget(self.current_thinking)
            self.current_thinking.deleteLater()
            self.current_thinking = None
    
    def clear_messages(self):
        """Clear all messages"""
        while self.message_layout.count() > 1:  # Keep stretch
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        from PyQt6.QtCore import QPoint
        if event.button() == Qt.MouseButton.LeftButton:
            # Only allow dragging on empty areas (not on interactive elements)
            widget = self.childAt(event.position().toPoint())
            if widget:
                # Check if it's an interactive widget
                while widget:
                    if isinstance(widget, (QPushButton, QTextEdit, QScrollArea, QLabel)):
                        # Check if it's a message label (allow dragging on message area background)
                        if isinstance(widget, QLabel):
                            # Allow dragging on message area background, but not on message text
                            parent = widget.parent()
                            if parent and hasattr(parent, 'setStyleSheet'):
                                # It's likely a message bubble, allow drag
                                pass
                            else:
                                return super().mousePressEvent(event)
                        else:
                            return super().mousePressEvent(event)
                    widget = widget.parent()
            
            # Start dragging
            parent_window = self.window()
            if parent_window:
                self.drag_position = event.globalPosition().toPoint() - parent_window.frameGeometry().topLeft()
                event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        from PyQt6.QtCore import QPoint
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            parent_window = self.window()
            if parent_window:
                parent_window.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Mouse release event - reset drag position"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
        super().mouseReleaseEvent(event)
    
    def _add_status_indicator(self):
        """Add emotional status indicator"""
        status_widget = QWidget()
        status_widget.setStyleSheet(STATUS_INDICATOR)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)
        
        # Status icon
        icon = QLabel("✨")
        icon.setStyleSheet("font-size: 16px; background: transparent; padding: 0px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(icon)
        
        # Status text
        status_text = QLabel("I'm here for you")
        status_text.setStyleSheet(STATUS_TEXT)
        status_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(status_text)
        
        status_layout.addStretch()
        
        # Insert at the beginning (before stretch)
        self.message_layout.insertWidget(0, status_widget)
        
        # Auto-hide after 3 seconds
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._hide_status_indicator(status_widget))
        timer.start(3000)
    
    def _hide_status_indicator(self, widget):
        """Hide status indicator with fade effect"""
        if widget:
            self.message_layout.removeWidget(widget)
            widget.deleteLater()

