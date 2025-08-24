"""
Plant Facts Explorer - Main Application
A modular Streamlit app for plant identification and information
Author: Maniwar
Version: 2.0.0 - Updated for Streamlit 2025
"""

import streamlit as st
import base64
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Clear any stale cache
if 'initialized' not in st.session_state:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.initialized = True

# Import modules after clearing cache
from utils.config import AppConfig
from utils.ui_components import (
    render_header,
    render_custom_css,
    render_plant_analysis_display,
    render_legal_footer
)
from utils.plant_service import PlantService
from utils.search_service import get_search_suggestions
from utils.cache_service import CacheService
from streamlit_searchbox import st_searchbox

# Initialize configuration
config = AppConfig()

# Page configuration
st.set_page_config(
    layout="wide",
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON
)

# Initialize services without caching to avoid stale instances
def init_services():
    """Initialize service instances"""
    cache_service = CacheService()
    plant_service = PlantService(cache_service)
    return plant_service, cache_service

plant_service, cache_service = init_services()

# Verify service methods exist (for debugging)
if st.secrets.get("DEBUG", False):
    required_methods = ['is_ready', 'get_cached_analysis', 'get_analysis_stream', 'identify_plant_from_image']
    for method in required_methods:
        if not hasattr(plant_service, method):
            st.error(f"Missing method: {method}")
        else:
            st.success(f"✓ Method exists: {method}")

# Check if services are ready
if not plant_service.is_ready():
    st.error("⚠️ OpenAI API not configured. Please add OPENAI_API_KEY to your secrets.")
    st.stop()

# Apply minimal custom CSS
render_custom_css()

# Render header
render_header()

# Show cache status in sidebar (for debugging)
with st.sidebar:
    st.markdown("### 🔧 System Status")
    if cache_service.is_connected():
        st.success("✅ Cache: Connected")
        
        # Cache testing section
        with st.expander("Cache Debug"):
            test_plant = st.text_input("Check if plant is cached:", placeholder="e.g., Rose")
            if test_plant:
                # Normalize for consistent checking
                test_plant_normalized = test_plant.strip().title()
                if plant_service.get_cached_analysis(test_plant_normalized):
                    st.success(f"✅ '{test_plant_normalized}' is cached")
                    # Add clear cache button for testing
                    if st.button("Clear this cache entry", key="clear_cache"):
                        cache_key = f"{config.CACHE_KEY_PREFIX}{test_plant_normalized}"
                        if cache_service.delete(cache_key):
                            st.info(f"Cleared cache for '{test_plant_normalized}'")
                            st.rerun()
                else:
                    st.info(f"❌ '{test_plant_normalized}' not in cache")
    else:
        st.warning("⚠️ Cache: Disabled")
        st.caption("App works without caching")
        with st.expander("Redis Setup Help"):
            st.markdown("""
            **Options to enable caching:**
            1. **Local Redis**: `docker run -p 6379:6379 redis`
            2. **Redis Cloud**: Free tier at redis.com
            3. **Upstash**: Serverless Redis at upstash.com
            
            Add to `.streamlit/secrets.toml`:
            ```
            REDIS_HOST = "your-host"
            REDIS_PORT = 6379
            REDIS_PASSWORD = "your-password"
            ```
            """)
    
    st.divider()
    st.markdown("### 📊 App Info")
    st.caption(f"Version: {config.APP_VERSION}")
    st.caption(f"Author: {config.AUTHOR}")
    st.caption("Cache TTL: No expiration (permanent)")  # Cache never expires

# Input method selector with modern styling
with st.container():
    st.subheader("🎯 Choose Your Input Method")
    input_method = st.radio(
        "Select how you want to identify your plant:",
        config.INPUT_METHODS,
        horizontal=True,
        label_visibility="collapsed"
    )

# Search Box Method
if input_method == config.INPUT_METHODS[0]:  # "🔍 Search Box"
    with st.container(border=True):
        st.subheader("🔍 Search for Plants")
        
        # Use columns for search layout
        col1, col2 = st.columns([4, 1], gap="medium")
        
        with col1:
            plant_name = st_searchbox(
                search_function=get_search_suggestions,
                placeholder="e.g., Monstera Deliciosa, Rose, Cactus...",
                label=None,
                clear_on_submit=False,
                clearable=True,
                key="plant_search",
            )
        
        with col2:
            # Search button with proper width
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        mute_audio = st.checkbox("🔇 Mute Audio", value=True)
    
    if search_button and plant_name:
        try:
            # Normalize plant name for consistent caching
            plant_name = plant_name.strip().title()
            
            # Check cache first (with fallback for missing method)
            cached_analysis = None
            if hasattr(plant_service, 'get_cached_analysis'):
                cached_analysis = plant_service.get_cached_analysis(plant_name)
            
            if cached_analysis:
                # Display cached content instantly
                st.info("💾 Loading from cache - instant results!")
                analysis = cached_analysis
                # Show debug info in development
                if st.secrets.get("DEBUG", False):
                    st.caption(f"Cache hit: {len(cached_analysis)} characters")
            else:
                # Stream new content
                with st.spinner("🌿 Analyzing plant information..."):
                    if hasattr(plant_service, 'get_analysis_stream'):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                    else:
                        st.error("PlantService missing required methods. Please refresh the page.")
                        st.stop()
                st.success("✅ Analysis complete and cached for future use!")
            
            # Display the analysis
            st.divider()
            render_plant_analysis_display(plant_name, analysis, mute_audio)
            
        except Exception as e:
            st.error(f"❌ Error analyzing plant: {str(e)}")

# File Upload Method
elif input_method == config.INPUT_METHODS[1]:  # "📁 File Upload"
    with st.container(border=True):
        st.subheader("📁 Upload Plant Image")
        
        uploaded_image = st.file_uploader(
            "Drop an image or click to browse",
            type=['jpg', 'jpeg', 'png'],
            help="Supported formats: JPG, PNG"
        )
    
    if uploaded_image:
        col1, col2 = st.columns([1, 2], gap="medium")
        
        with col1:
            st.image(uploaded_image, caption='Uploaded Image', use_container_width=True)
        
        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_bytes = uploaded_image.read()
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Check cache status (with method check)
                cached_analysis = None
                try:
                    cached_analysis = plant_service.get_cached_analysis(plant_name)
                except AttributeError:
                    st.warning("Cache methods not available. Please refresh the page.")
                    cached_analysis = None
                
                if cached_analysis:
                    # Display cached content instantly
                    st.info("💾 Loading from cache - instant results!")
                    analysis = cached_analysis
                    # Show debug info in development
                    if st.secrets.get("DEBUG", False):
                        st.caption(f"Cache hit: {len(cached_analysis)} characters")
                else:
                    # Stream new content
                    with st.spinner("🌿 Fetching detailed information..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                    st.success("✅ Analysis complete and cached for future use!")
            
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
        
        # Display analysis if successful
        if 'analysis' in locals():
            st.divider()
            render_plant_analysis_display(plant_name, analysis)

# Camera Capture Method
elif input_method == config.INPUT_METHODS[2]:  # "📸 Camera Capture"
    with st.container(border=True):
        st.subheader("📸 Capture Plant Image")
        
        captured_image = st.camera_input("Take a photo of your plant")
    
    if captured_image:
        col1, col2 = st.columns([1, 2], gap="medium")
        
        with col1:
            st.image(captured_image, caption='Captured Image', use_container_width=True)
        
        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_bytes = captured_image.read()
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Check cache status (with method check)
                cached_analysis = None
                try:
                    cached_analysis = plant_service.get_cached_analysis(plant_name)
                except AttributeError:
                    st.warning("Cache methods not available. Please refresh the page.")
                    cached_analysis = None
                
                if cached_analysis:
                    # Display cached content instantly
                    st.info("💾 Loading from cache - instant results!")
                    analysis = cached_analysis
                    # Show debug info in development
                    if st.secrets.get("DEBUG", False):
                        st.caption(f"Cache hit: {len(cached_analysis)} characters")
                else:
                    # Stream new content
                    with st.spinner("🌿 Fetching detailed information..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                    st.success("✅ Analysis complete and cached for future use!")
            
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
        
        # Display analysis if successful
        if 'analysis' in locals():
            st.divider()
            render_plant_analysis_display(plant_name, analysis)

# Footer
render_legal_footer()
