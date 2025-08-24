"""
Utils Package
Contains all utility modules for the Plant Facts Explorer application
Author: Maniwar
"""

# Import main components for easier access
from .config import AppConfig
from .cache_service import CacheService
from .plant_service import PlantService
from .search_service import get_search_suggestions
from .ui_components import (
    render_header,
    render_custom_css,
    render_plant_analysis_display,
    render_legal_footer,
    get_plant_image,
    extract_quick_facts,
    clean_text_for_tts
)

# Package metadata
__version__ = "2.0.0"
__author__ = "Maniwar"

# Define what should be imported with "from utils import *"
__all__ = [
    'AppConfig',
    'CacheService',
    'PlantService',
    'get_search_suggestions',
    'render_header',
    'render_custom_css',
    'render_plant_analysis_display',
    'render_legal_footer',
    'get_plant_image',
    'extract_quick_facts',
    'clean_text_for_tts'
]
