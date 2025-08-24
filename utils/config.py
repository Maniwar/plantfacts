"""
Configuration module for Plant Facts Explorer
Central place for all app configuration and constants
Author: Maniwar
"""

class AppConfig:
    """Application configuration class"""
    
    # App Settings
    PAGE_TITLE = "Plant Facts Explorer"
    PAGE_ICON = "🌿"
    APP_VERSION = "2.1.0"  # Updated: Fixed streaming and caching
    AUTHOR = "Maniwar"
    
    # Input Methods
    INPUT_METHODS = ["🔍 Search Box", "📁 File Upload", "📸 Camera Capture"]
    
    # OpenAI Settings
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 4096
    
    # Redis Cache Settings
    CACHE_KEY_PREFIX = "plant:"
    CACHE_TTL = None  # No expiration - cache forever
    
    # UI Settings
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 600
    
    # Plant Analysis Prompt Template
    ANALYSIS_PROMPT = """Write a comprehensive and detailed report on the plant {plant_name}. Include the following information:
1. **General Information**:
   - Common name
   - Scientific name
   - Origin and habitat
   - Description and physical characteristics

2. **Care Instructions**:
   - Light requirements
   - Watering needs
   - Soil preferences
   - Temperature and humidity requirements
   - Fertilization tips
   - Pruning and maintenance

3. **Toxicity**:
   - Is the plant toxic to humans or pets?
   - Symptoms of poisoning
   - What you should do

4. **Propagation**:
   - Methods of propagation
   - Best time to propagate

5. **Common Issues**:
   - Pests and diseases
   - Common problems and solutions

6. **Interesting Facts**:
   - Any unique features or historical significance

Make sure the report is detailed and easy to understand for both novice and experienced plant enthusiasts."""

    # Plant Identification Prompt
    IDENTIFICATION_PROMPT = "Reply with only the plant name and its scientific name. Example: Chinese Rose (Rosa chinensis)"
    
    # Quick Facts Patterns
    LIGHT_PATTERNS = ["full sun", "partial shade", "full shade", "bright indirect", "low light"]
    WATER_PATTERNS = {
        "daily": "Daily",
        "weekly": "Weekly", 
        "moderate": "Moderate"
    }
    
    # Legal Text (abbreviated for readability)
    LEGAL_DISCLAIMER = """This application ("App") is provided "as is" without any warranties..."""
