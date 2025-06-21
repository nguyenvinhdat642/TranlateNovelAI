"""
GUI modules for TranslateNovelAI

Contains all user interface implementations:
- gui_web.py: Modern web interface using Gradio
- gui_modern.py: Modern desktop interface using CustomTkinter  
- gui_simple.py: Classic desktop interface using Tkinter
- custom_dialogs.py: Custom dialog and notification system
"""

try:
    from .gui_web import launch_web_gui
    WEB_GUI_AVAILABLE = True
except ImportError:
    WEB_GUI_AVAILABLE = False

try:
    from .gui_modern import ModernTranslateNovelAI
    MODERN_GUI_AVAILABLE = True
except ImportError:
    MODERN_GUI_AVAILABLE = False

try:
    from .gui_simple import TranslateNovelAI
    CLASSIC_GUI_AVAILABLE = True
except ImportError:
    CLASSIC_GUI_AVAILABLE = False

try:
    from .custom_dialogs import (
        show_success, show_error, show_warning, show_question,
        show_toast_success, show_toast_error, show_toast_warning, show_toast_info
    )
    CUSTOM_DIALOGS_AVAILABLE = True
except ImportError:
    CUSTOM_DIALOGS_AVAILABLE = False

__all__ = [
    'launch_web_gui',
    'ModernTranslateNovelAI', 
    'TranslateNovelAI',
    'show_success',
    'show_error',
    'show_warning', 
    'show_question',
    'show_toast_success',
    'show_toast_error',
    'show_toast_warning',
    'show_toast_info',
    'WEB_GUI_AVAILABLE',
    'MODERN_GUI_AVAILABLE',
    'CLASSIC_GUI_AVAILABLE',
    'CUSTOM_DIALOGS_AVAILABLE'
] 