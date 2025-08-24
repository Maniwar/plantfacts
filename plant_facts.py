"""
Plant Facts Explorer - Main Application
A modular Streamlit app for plant identification and information
Author: Maniwar
Version: 2.6.0 - Fixed particles and image handling
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

# Import streamlit_searchbox first
from streamlit_searchbox import st_searchbox

# Import utils modules directly
from utils.config import AppConfig
from utils.cache_service import CacheService
from utils.plant_service import PlantService
from utils.search_service import get_search_suggestions
from utils.ui_components import (
    render_header,
    render_custom_css,
    render_plant_analysis_display,
    render_legal_footer
)

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

# Check if services are ready
if not plant_service.is_ready():
    st.error("⚠️ OpenAI API not configured. Please add OPENAI_API_KEY to your secrets.")
    st.stop()

# Apply minimal custom CSS
render_custom_css()

# Render header
render_header()

# Show cache status at the top (no sidebar)
with st.expander("🔧 System Status", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if cache_service.is_connected():
            st.success("✅ Cache: Connected")
        else:
            st.warning("⚠️ Cache: Running without caching")
            st.caption("Redis not configured - app works but responses won't be cached")
    
    with col2:
        st.info(f"📊 Version: {config.APP_VERSION}")
    
    with col3:
        st.info(f"👤 Author: {config.AUTHOR}")
    
    # Advanced cache debug (only if connected)
    if cache_service.is_connected():
        with st.container():
            st.divider()
            test_plant = st.text_input("🔍 Check if plant is cached:", placeholder="e.g., Rose", key="cache_check")
            if test_plant:
                test_plant_normalized = test_plant.strip().title()
                if plant_service.get_cached_analysis(test_plant_normalized):
                    st.success(f"✅ '{test_plant_normalized}' is in cache")
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        if st.button("🗑️ Clear this cache entry", key="clear_cache"):
                            cache_key = f"{config.CACHE_KEY_PREFIX}{test_plant_normalized}"
                            if cache_service.delete(cache_key):
                                st.info(f"Cleared cache for '{test_plant_normalized}'")
                                st.rerun()
                else:
                    st.info(f"❌ '{test_plant_normalized}' not cached yet")

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
            
            # Create a placeholder for the content
            content_placeholder = st.empty()
            
            # Check cache first
            cached_analysis = plant_service.get_cached_analysis(plant_name)
            
            if cached_analysis:
                # Display cached content instantly in formatted view
                if cache_service.is_connected():
                    st.info("💾 Loading from cache - instant results!")
                analysis = cached_analysis
            else:
                # Stream new content into a temporary container
                st.info("🌿 Generating new analysis...")
                
                # Use a container for streaming that will be replaced
                with content_placeholder.container():
                    st.markdown("### 🔍 Live Analysis Stream")
                    analysis = ""
                    stream_container = st.empty()
                    
                    # Stream the content and accumulate it
                    for chunk in plant_service.get_analysis_stream(plant_name):
                        analysis += chunk
                        # Update the streaming display
                        with stream_container.container():
                            st.markdown(analysis)
                
                # Clear the placeholder after streaming is complete
                content_placeholder.empty()
                if cache_service.is_connected():
                    st.success("✅ Analysis complete and cached for future use!")
                else:
                    st.success("✅ Analysis complete!")
            
            # Display the formatted analysis (no uploaded image for search)
            st.divider()
            render_plant_analysis_display(plant_name, analysis, mute_audio)
            
        except Exception as e:
            st.error(f"❌ Error analyzing plant: {str(e)}")
            logging.error(f"Search error: {str(e)}")

# File Upload Method
elif input_method == config.INPUT_METHODS[1]:  # "📁 File Upload"
    with st.container(border=True):
        st.subheader("📁 Upload Plant Image")
        
        uploaded_image = st.file_uploader(
            "Drop an image or click to browse",
            type=['jpg', 'jpeg', 'png'],
            help="Supported formats: JPG, PNG"
        )
        
        mute_audio = st.checkbox("🔇 Mute Audio", value=True, key="mute_upload")
    
    if uploaded_image:
        # Read image bytes once
        image_bytes = uploaded_image.read()
        uploaded_image.seek(0)  # Reset for potential re-reading
        
        col1, col2 = st.columns([1, 2], gap="medium")
        
        with col1:
            st.image(image_bytes, caption='Uploaded Image', use_container_width=True)
        
        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Create placeholder for content
                content_placeholder = st.empty()
                
                # Check cache status
                cached_analysis = plant_service.get_cached_analysis(plant_name)
                
                if cached_analysis:
                    # Display cached content instantly
                    if cache_service.is_connected():
                        st.info("💾 Loading from cache - instant results!")
                    analysis = cached_analysis
                else:
                    # Stream new content
                    st.info("🌿 Generating detailed information...")
                    
                    with content_placeholder.container():
                        st.markdown("### 🔍 Live Analysis Stream")
                        analysis = ""
                        stream_container = st.empty()
                        
                        for chunk in plant_service.get_analysis_stream(plant_name):
                            analysis += chunk
                            with stream_container.container():
                                st.markdown(analysis)
                    
                    content_placeholder.empty()
                    if cache_service.is_connected():
                        st.success("✅ Analysis complete and cached for future use!")
                    else:
                        st.success("✅ Analysis complete!")
            
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
                logging.error(f"Image processing error: {str(e)}")
        
        # Display formatted analysis with the uploaded image
        if 'analysis' in locals():
            st.divider()
            render_plant_analysis_display(
                plant_name, 
                analysis, 
                mute_audio,
                uploaded_image_bytes=image_bytes  # Pass the uploaded image
            )

# Camera Capture Method
elif input_method == config.INPUT_METHODS[2]:  # "📸 Camera Capture"
    with st.container(border=True):
        st.subheader("📸 Capture Plant Image")
        
        captured_image = st.camera_input("Take a photo of your plant")
        mute_audio = st.checkbox("🔇 Mute Audio", value=True, key="mute_camera")
    
    if captured_image:
        # Read image bytes once
        image_bytes = captured_image.read()
        captured_image.seek(0)  # Reset for potential re-reading
        
        col1, col2 = st.columns([1, 2], gap="medium")
        
        with col1:
            st.image(image_bytes, caption='Captured Image', use_container_width=True)
        
        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Create placeholder for content
                content_placeholder = st.empty()
                
                # Check cache status
                cached_analysis = plant_service.get_cached_analysis(plant_name)
                
                if cached_analysis:
                    # Display cached content instantly
                    if cache_service.is_connected():
                        st.info("💾 Loading from cache - instant results!")
                    analysis = cached_analysis
                else:
                    # Stream new content
                    st.info("🌿 Generating detailed information...")
                    
                    with content_placeholder.container():
                        st.markdown("### 🔍 Live Analysis Stream")
                        analysis = ""
                        stream_container = st.empty()
                        
                        for chunk in plant_service.get_analysis_stream(plant_name):
                            analysis += chunk
                            with stream_container.container():
                                st.markdown(analysis)
                    
                    content_placeholder.empty()
                    if cache_service.is_connected():
                        st.success("✅ Analysis complete and cached for future use!")
                    else:
                        st.success("✅ Analysis complete!")
            
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
                logging.error(f"Camera capture error: {str(e)}")
        
        # Display formatted analysis with the captured image
        if 'analysis' in locals():
            st.divider()
            render_plant_analysis_display(
                plant_name, 
                analysis, 
                mute_audio,
                uploaded_image_bytes=image_bytes  # Pass the captured image
            )

# Footer
render_legal_footer()