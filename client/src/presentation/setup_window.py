"""
Setup window - Large centered window for personality setup
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QMouseEvent
# Compatible with relative and absolute imports
try:
    from .ui_styles_refined import SETUP_WINDOW_STYLE
except ImportError:
    from ui_styles_refined import SETUP_WINDOW_STYLE


class SetupWindow(QWidget):
    """Large centered setup window for personality configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()
        self._setup_window()
    
    def _setup_window(self):
        """Set up window properties"""
        # Set window size (larger for settings)
        self.setFixedSize(600, 700)
        
        # Set window flags: always-on-top + frameless
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        
        # Set window style
        self.setStyleSheet(SETUP_WINDOW_STYLE)
        
        # Center window on screen
        self._center_on_screen()
    
    def _center_on_screen(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.frameGeometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press event for window dragging"""
        # Check if clicked on a child widget that should not trigger drag
        widget = self.childAt(event.position().toPoint())
        if widget:
            # Check if it's a button or inside a button
            while widget:
                if isinstance(widget, QPushButton):
                    return super().mousePressEvent(event)
                widget = widget.parent()
        
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Mouse move event to implement window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def set_content(self, widget: QWidget):
        """Set content widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget)

