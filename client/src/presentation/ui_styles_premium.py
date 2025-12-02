"""
Premium UI Design System
Inspired by modern apps: Linear, Notion, Discord, macOS
Features: Glassmorphism, minimalism, micro-interactions
"""
from PyQt6.QtCore import Qt

# Premium color palette - Soft, elegant, modern
COLORS = {
    # Primary - Soft purple gradient (like Linear)
    "primary": "#8b5cf6",
    "primary_light": "#a78bfa",
    "primary_dark": "#7c3aed",
    "primary_gradient_start": "#8b5cf6",
    "primary_gradient_end": "#ec4899",
    
    # Accents
    "accent_blue": "#3b82f6",
    "accent_pink": "#ec4899",
    "accent_amber": "#f59e0b",
    "accent": "#ec4899",  # Add accent for personality_setup_window
    
    # Backgrounds - Glassmorphism
    "bg_primary": "rgba(255, 255, 255, 0.85)",  # Frosted glass
    "bg_secondary": "rgba(248, 250, 252, 0.9)",
    "bg_tertiary": "rgba(241, 245, 249, 0.95)",
    "bg_hover": "rgba(255, 255, 255, 0.95)",
    
    # Surfaces - Card-like
    "surface": "rgba(255, 255, 255, 0.7)",
    "surface_elevated": "rgba(255, 255, 255, 0.9)",
    "surface_hover": "rgba(255, 255, 255, 0.8)",
    
    # Borders - Subtle
    "border_light": "rgba(226, 232, 240, 0.5)",
    "border_medium": "rgba(203, 213, 225, 0.6)",
    "border_strong": "rgba(148, 163, 184, 0.4)",
    
    # Text - High contrast but soft
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_tertiary": "#94a3b8",
    "text_inverse": "#ffffff",
    
    # Shadows - Layered, soft
    "shadow_sm": "rgba(15, 23, 42, 0.04)",
    "shadow_md": "rgba(15, 23, 42, 0.08)",
    "shadow_lg": "rgba(15, 23, 42, 0.12)",
    "shadow_xl": "rgba(15, 23, 42, 0.16)",
    
    # Status colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
}

# Main window - Glassmorphism effect
MAIN_WINDOW_STYLE = f"""
    QWidget {{
        background: {COLORS["bg_primary"]};
        border-radius: 24px;
        border: 1px solid {COLORS["border_light"]};
    }}
"""

# Setup window - Elevated card
SETUP_WINDOW_STYLE = f"""
    QWidget {{
        background: {COLORS["bg_secondary"]};
        border-radius: 28px;
        border: 1px solid {COLORS["border_light"]};
    }}
"""

# Control bar - Minimal, elegant
CONTROL_BAR_STYLE = f"""
    QWidget {{
        background: transparent;
        border-top-left-radius: 24px;
        border-top-right-radius: 24px;
        border-bottom: 1px solid {COLORS["border_light"]};
    }}
"""

# Premium buttons - Soft gradients, smooth
PRIMARY_BUTTON = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary_gradient_start"]}, 
            stop:1 {COLORS["primary_gradient_end"]});
        color: {COLORS["text_inverse"]};
        border: none;
        border-radius: 14px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary_dark"]}, 
            stop:1 {COLORS["primary_gradient_end"]});
    }}
    QPushButton:pressed {{
        padding-top: 15px;
        padding-bottom: 13px;
    }}
"""

SECONDARY_BUTTON = f"""
    QPushButton {{
        background: {COLORS["surface"]};
        color: {COLORS["text_primary"]};
        border: 1.5px solid {COLORS["border_medium"]};
        border-radius: 14px;
        padding: 14px 28px;
        font-weight: 500;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
    QPushButton:hover {{
        background: {COLORS["surface_hover"]};
        border-color: {COLORS["primary_light"]};
    }}
    QPushButton:pressed {{
        background: {COLORS["bg_tertiary"]};
    }}
"""

ICON_BUTTON = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary_gradient_start"]}, 
            stop:1 {COLORS["primary_gradient_end"]});
        color: {COLORS["text_inverse"]};
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary_dark"]}, 
            stop:1 {COLORS["primary_gradient_end"]});
    }}
"""

# Input fields - Clean, focused
INPUT_FIELD = f"""
    QTextEdit {{
        background: {COLORS["surface"]};
        border: 1.5px solid {COLORS["border_medium"]};
        border-radius: 16px;
        padding: 14px 18px;
        font-size: 14px;
        color: {COLORS["text_primary"]};
        selection-background-color: {COLORS["primary_light"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
        line-height: 1.5;
    }}
    QTextEdit:focus {{
        background: {COLORS["bg_hover"]};
        border: 2px solid {COLORS["primary"]};
        padding: 13px 17px;
    }}
"""

COMPACT_INPUT = f"""
    QTextEdit {{
        background: {COLORS["surface"]};
        border: 1.5px solid {COLORS["border_medium"]};
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 13px;
        color: {COLORS["text_primary"]};
        selection-background-color: {COLORS["primary_light"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
    QTextEdit:focus {{
        background: {COLORS["bg_hover"]};
        border: 2px solid {COLORS["primary"]};
        padding: 9px 13px;
    }}
"""

# Scroll areas - Minimal
SCROLL_AREA = f"""
    QScrollArea {{
        border: 1px solid {COLORS["border_light"]};
        border-radius: 20px;
        background: {COLORS["bg_secondary"]};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 5px;
        border-radius: 2.5px;
        margin: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS["border_strong"]};
        border-radius: 2.5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS["text_tertiary"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# Message bubbles - Modern, rounded
USER_MESSAGE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary_gradient_start"]}, 
            stop:1 {COLORS["primary_gradient_end"]});
        border-radius: 18px 18px 6px 18px;
        max-width: 250px;
    }}
"""

AI_MESSAGE = f"""
    QWidget {{
        background: {COLORS["surface_elevated"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: 18px 18px 18px 6px;
        max-width: 250px;
    }}
"""

# Example cards - Clickable, elegant
EXAMPLE_CARD = f"""
    QPushButton {{
        background: {COLORS["surface"]};
        border: 1.5px solid {COLORS["border_light"]};
        border-radius: 16px;
        padding: 16px 20px;
        text-align: left;
        font-size: 13px;
        color: {COLORS["text_primary"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
    QPushButton:hover {{
        background: {COLORS["surface_hover"]};
        border-color: {COLORS["primary_light"]};
        transform: translateY(-1px);
    }}
"""

# Typography
TITLE_LARGE = f"""
    QLabel {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
        line-height: 1.2;
    }}
"""

TITLE_MEDIUM = f"""
    QLabel {{
        font-size: 20px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.4px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
"""

BODY_TEXT = f"""
    QLabel {{
        font-size: 14px;
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
"""

LABEL_TEXT = f"""
    QLabel {{
        font-size: 13px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
"""

CAPTION_TEXT = f"""
    QLabel {{
        font-size: 12px;
        color: {COLORS["text_tertiary"]};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
"""

# Control buttons - Minimal, modern
MINIMIZE_BTN = f"""
    QPushButton {{
        background: {COLORS["accent_amber"]};
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: #d97706;
    }}
"""

CLOSE_BTN = f"""
    QPushButton {{
        background: {COLORS["error"]};
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: #dc2626;
    }}
"""

# Thinking indicator
THINKING_TEXT = f"""
    QLabel {{
        color: {COLORS["text_secondary"]};
        font-size: 13px;
        font-style: italic;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
    }}
"""

