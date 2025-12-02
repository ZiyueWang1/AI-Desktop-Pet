"""
Refined UI Design System - Low-disturbance, High-readability
Glassmorphism-inspired design for AI Desktop Pet
"""
from PyQt6.QtCore import Qt

# Refined color palette - Minimal, unobtrusive
COLORS = {
    # Primary - Used sparingly, very light versions
    "primary": "#8b5cf6",
    "primary_light": "rgba(139, 92, 246, 0.12)",  # 12% opacity for user messages
    "primary_medium": "rgba(139, 92, 246, 0.15)",  # 15% for buttons
    "primary_hover": "rgba(139, 92, 246, 0.25)",  # 25% on hover
    "primary_focus": "rgba(139, 92, 246, 0.4)",   # 40% for focus
    
    # Backgrounds - Glassmorphism
    "bg_main": "rgba(255, 255, 255, 0.92)",       # 92% opacity
    "bg_secondary": "rgba(248, 250, 252, 0.95)",  # 95% opacity
    "bg_input": "rgba(248, 250, 252, 0.8)",      # 80% opacity
    "bg_hover": "rgba(255, 255, 255, 0.98)",
    
    # Surfaces
    "surface_ai": "rgba(248, 250, 252, 0.95)",   # AI message background
    "surface_user": "rgba(139, 92, 246, 0.12)",  # User message background
    
    # Borders - Very subtle
    "border_light": "rgba(226, 232, 240, 0.5)",
    "border_medium": "rgba(226, 232, 240, 0.6)",
    "border_focus": "rgba(139, 92, 246, 0.4)",
    
    # Text
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_tertiary": "rgba(148, 163, 184, 0.6)",
    
    # Status
    "status_online": "#10b981",
    "status_thinking": "#8b5cf6",
}

# Main window - Enhanced glassmorphism with gradient
MAIN_WINDOW = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(255, 255, 255, 0.95),
            stop:1 rgba(248, 250, 252, 0.92));
        border-radius: 26px;
        border: 1.5px solid rgba(139, 92, 246, 0.15);
    }}
"""

# Setup window style
SETUP_WINDOW_STYLE = f"""
    QWidget {{
        background: {COLORS["bg_main"]};
        border-radius: 28px;
        border: 1px solid {COLORS["border_light"]};
    }}
"""

# Control bar - Minimal with subtle background
CONTROL_BAR = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(255, 255, 255, 0.98),
            stop:1 rgba(248, 250, 252, 0.95));
        border-top-left-radius: 24px;
        border-top-right-radius: 24px;
        border-bottom: 1px solid {COLORS["border_light"]};
    }}
"""

# Scroll area - Enhanced with gradient background
SCROLL_AREA = f"""
    QScrollArea {{
        border: 1.5px solid {COLORS["border_medium"]};
        border-radius: 22px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(248, 250, 252, 0.95),
            stop:1 rgba(241, 245, 249, 0.98));
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border-radius: 3px;
        margin: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(139, 92, 246, 0.3);
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(139, 92, 246, 0.5);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# AI Message Bubble - Elegant with subtle shadow effect
AI_MESSAGE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(255, 255, 255, 0.98),
            stop:1 rgba(248, 250, 252, 0.95));
        border: 1px solid {COLORS["border_medium"]};
        border-radius: 18px 18px 18px 6px;
        max-width: 280px;
        padding: 0px;
    }}
"""

# User Message Bubble - Beautiful gradient background
USER_MESSAGE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(139, 92, 246, 0.15),
            stop:1 rgba(96, 165, 250, 0.15));
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 18px 18px 6px 18px;
        max-width: 280px;
        padding: 0px;
    }}
"""

# Message text style
MESSAGE_TEXT = f"""
    QLabel {{
        color: {COLORS["text_primary"]};
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
        background: transparent;
    }}
"""

# Input container - Unified design with enhanced visual
INPUT_CONTAINER = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(255, 255, 255, 0.85),
            stop:1 rgba(248, 250, 252, 0.9));
        border: 1.5px solid {COLORS["border_medium"]};
        border-radius: 18px;
        padding: 6px;
    }}
"""

# Input field - No border, transparent background
INPUT_FIELD = f"""
    QTextEdit {{
        background: transparent;
        border: none;
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 14px;
        color: {COLORS["text_primary"]};
        selection-background-color: {COLORS["primary_light"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
    QTextEdit:focus {{
        background: {COLORS["bg_hover"]};
    }}
"""

# Send button - Beautiful gradient with icon
SEND_BUTTON = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #8b5cf6,
            stop:1 #6366f1);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 20px;
        min-width: 44px;
        min-height: 44px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7c3aed,
            stop:1 #4f46e5);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6d28d9,
            stop:1 #4338ca);
        padding-top: 2px;
    }}
"""

# Status indicator - Fixed border and padding
STATUS_INDICATOR = f"""
    QWidget {{
        background: {COLORS["bg_secondary"]};
        border: 1.5px solid {COLORS["border_light"]};
        border-radius: 16px;
        padding: 10px 14px;
        margin: 0px;
    }}
"""

STATUS_TEXT = f"""
    QLabel {{
        color: {COLORS["text_secondary"]};
        font-size: 13px;
        font-weight: 500;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
        background: transparent;
    }}
"""

# Control buttons - Enhanced with smooth gradients
MINIMIZE_BTN = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #fbbf24,
            stop:1 #f59e0b);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #f59e0b,
            stop:1 #d97706);
    }}
    QPushButton:pressed {{
        padding-top: 1px;
    }}
"""

CLOSE_BTN = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #f87171,
            stop:1 #ef4444);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #ef4444,
            stop:1 #dc2626);
    }}
    QPushButton:pressed {{
        padding-top: 1px;
    }}
"""

