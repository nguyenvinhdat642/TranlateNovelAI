"""
Assets package for TranslateNovelAI

Contains application resources:
- create_icon.py: Icon generation script
- app_icon.ico: Main application icon
- success_icon.png: Success notification icon
- Various sized PNG icons for different platforms
"""

import os

ASSETS_DIR = os.path.dirname(__file__)
APP_ICON = os.path.join(ASSETS_DIR, "app_icon.ico")
SUCCESS_ICON = os.path.join(ASSETS_DIR, "success_icon.png")

def get_icon_path(icon_name):
    """Get path to icon file"""
    return os.path.join(ASSETS_DIR, icon_name) 