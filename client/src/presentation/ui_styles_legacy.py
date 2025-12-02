"""
Modern UI styles for the application
Centralized style definitions for consistent, beautiful UI
"""

# Modern color palette
COLORS = {
    "primary": "#6366f1",  # Indigo - modern primary color
    "primary_hover": "#4f46e5",
    "primary_light": "#818cf8",
    "secondary": "#8b5cf6",  # Purple
    "success": "#10b981",  # Green
    "warning": "#f59e0b",  # Amber
    "danger": "#ef4444",  # Red
    "background": "#ffffff",
    "background_alt": "#f8fafc",
    "surface": "#ffffff",
    "surface_hover": "#f1f5f9",
    "border": "#e2e8f0",
    "border_focus": "#6366f1",
    "text_primary": "#1e293b",
    "text_secondary": "#64748b",
    "text_tertiary": "#94a3b8",
    "shadow": "rgba(0, 0, 0, 0.1)",
    "shadow_hover": "rgba(0, 0, 0, 0.15)",
}

# Window styles
WINDOW_STYLE = f"""
    QWidget {{
        background-color: {COLORS["background"]};
        border-radius: 16px;
    }}
"""

CONTROL_BAR_STYLE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS["background_alt"]}, 
            stop:1 {COLORS["background"]});
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
        border-bottom: 1px solid {COLORS["border"]};
    }}
"""

# Button styles
PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS["primary"]}, 
            stop:1 {COLORS["primary_hover"]});
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS["primary_hover"]}, 
            stop:1 {COLORS["primary"]});
    }}
    QPushButton:pressed {{
        background: {COLORS["primary_hover"]};
        padding-top: 11px;
        padding-bottom: 9px;
    }}
"""

SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS["background_alt"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {COLORS["surface_hover"]};
        border-color: {COLORS["primary_light"]};
    }}
    QPushButton:pressed {{
        background-color: {COLORS["border"]};
    }}
"""

# Input field styles
INPUT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS["background"]};
        border: 2px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
        color: {COLORS["text_primary"]};
        selection-background-color: {COLORS["primary_light"]};
    }}
    QTextEdit:focus {{
        border: 2px solid {COLORS["border_focus"]};
        background-color: {COLORS["background"]};
    }}
"""

# Scroll area styles
SCROLL_AREA_STYLE = f"""
    QScrollArea {{
        border: 2px solid {COLORS["border"]};
        border-radius: 12px;
        background-color: {COLORS["background_alt"]};
    }}
    QScrollBar:vertical {{
        background: {COLORS["background_alt"]};
        width: 8px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS["border"]};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS["text_tertiary"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# Message bubble styles
USER_MESSAGE_STYLE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS["primary"]}, 
            stop:1 {COLORS["primary_hover"]});
        border-radius: 12px;
        max-width: 220px;
    }}
"""

AI_MESSAGE_STYLE = f"""
    QWidget {{
        background-color: {COLORS["surface_hover"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        max-width: 220px;
    }}
"""

# Title styles
TITLE_STYLE = f"""
    QLabel {{
        font-size: 22px;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.5px;
    }}
"""

SUBTITLE_STYLE = f"""
    QLabel {{
        font-size: 13px;
        color: {COLORS["text_secondary"]};
        line-height: 1.5;
    }}
"""

LABEL_STYLE = f"""
    QLabel {{
        font-size: 12px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
    }}
"""

# Control buttons (minimize/close)
CONTROL_BUTTON_BASE = """
    QPushButton {
        border: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        opacity: 0.9;
    }
"""

MINIMIZE_BUTTON_STYLE = f"""
    {CONTROL_BUTTON_BASE}
    QPushButton {{
        background-color: {COLORS["warning"]};
        color: white;
    }}
    QPushButton:hover {{
        background-color: #d97706;
    }}
"""

CLOSE_BUTTON_STYLE = f"""
    {CONTROL_BUTTON_BASE}
    QPushButton {{
        background-color: {COLORS["danger"]};
        color: white;
    }}
    QPushButton:hover {{
        background-color: #dc2626;
    }}
"""

