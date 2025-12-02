"""
Main window module
Implements core floating window functionality: always-on-top, frameless, draggable
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from .ui_styles_refined import (
    MAIN_WINDOW, CONTROL_BAR, 
    MINIMIZE_BTN, CLOSE_BTN, COLORS
)


class FloatingWindow(QWidget):
    """Floating window class implementing always-on-top, frameless, draggable functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()
        self.settings_window = None
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Set window properties"""
        # Set window size - optimized for chat
        self.setFixedSize(500, 650)
        
        # Set window flags: always-on-top + frameless
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        
        # Enable translucent background for glassmorphism
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Set window style with glassmorphism
        self.setStyleSheet(MAIN_WINDOW)
        
        # Add soft shadow effect
        self._add_shadow_effect()
    
    def _setup_ui(self):
        """Set up UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top control bar
        control_bar = self._create_control_bar()
        layout.addWidget(control_bar)
        
        # Content area (set by subclass or externally)
        self.content_widget = QWidget()
        self.content_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        layout.addWidget(self.content_widget, 1)
    
    def _add_shadow_effect(self):
        """Add soft shadow effect to window"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))  # 12% opacity
        self.setGraphicsEffect(shadow)
    
    def _create_control_bar(self) -> QWidget:
        """Create top control bar (contains close and minimize buttons)"""
        bar = QWidget()
        bar.setFixedHeight(48)  # Taller for better dragging area
        bar.setStyleSheet(CONTROL_BAR)
        # Make control bar draggable (except buttons)
        bar.mousePressEvent = self._control_bar_press
        bar.mouseMoveEvent = self._control_bar_move
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 5, 5, 5)
        layout.setSpacing(8)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {COLORS["bg_input"]};
                border-radius: 16px;
            }}
        """)
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self._show_settings)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        # Minimize button
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(24, 24)
        minimize_btn.setStyleSheet(MINIMIZE_BTN)
        minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(CLOSE_BTN)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return bar
    
    def _control_bar_press(self, event):
        """Handle mouse press on control bar"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on a button - if so, don't drag
            widget = self.childAt(event.position().toPoint())
            if widget:
                # Check if it's a button or inside a button
                while widget:
                    if isinstance(widget, QPushButton):
                        return
                    widget = widget.parent()
            
            # Start dragging
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def _control_bar_move(self, event):
        """Handle mouse move on control bar"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def set_content(self, widget: QWidget):
        """Set content area"""
        layout = self.layout()
        # Remove old content widget
        if self.content_widget:
            layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()
        
        # Add new content widget
        self.content_widget = widget
        layout.addWidget(self.content_widget, 1)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press event for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on a button - if so, don't drag
            widget = self.childAt(event.position().toPoint())
            if widget:
                # Check if it's a button or inside a button
                while widget:
                    if isinstance(widget, QPushButton):
                        return super().mousePressEvent(event)
                    widget = widget.parent()
            
            # Start dragging
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Mouse move event to implement window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release event - reset drag position"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()
        super().mouseReleaseEvent(event)
    
    def closeEvent(self, event):
        """Window close event, save window position"""
        # Lazy import to avoid circular dependency
        try:
            from ..infrastructure.config_manager import ConfigManager
            config_manager = ConfigManager()
            config_manager.update_window_position(self.x(), self.y())
        except Exception:
            pass  # If config manager is unavailable, ignore error
        event.accept()
    
    def _show_settings(self):
        """Show settings window"""
        from .settings_window import SettingsWindow
        from .setup_window import SetupWindow
        
        # Create settings window in a modal setup window
        setup_win = SetupWindow()
        settings_content = SettingsWindow()
        settings_content.settings_changed.connect(self._on_settings_changed)
        setup_win.set_content(settings_content)
        
        # Store reference
        self.settings_window = setup_win
        
        setup_win.show()
    
    def _on_settings_changed(self):
        """Handle settings change"""
        # Reload settings and update UI
        # This will be handled by main.py
        pass

