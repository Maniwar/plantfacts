"""
Plant Facts Explorer - Main Application
A modular Streamlit app for plant identification and information
"""

import streamlit as st
import base64
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

# Initialize services
@st.cache_resource
def init_services():
    """Initialize and cache service instances"""
    cache_service = CacheService()
    plant_service = PlantService(cache_service)
    return plant_service, cache_service

plant_service, cache_service = init_services()

# Apply custom CSS
render_custom_css()

# Render header
render_header()

# Input method selector
st.markdown('<div class="input-selector">', unsafe_allow_html=True)
input_method = st.radio(
    "🎯 **Choose Your Input Method**",
    config.INPUT_METHODS,
    horizontal=True
)
st.markdown('</div>', unsafe_allow_html=True)

# Search Box Method
if input_method == config.INPUT_METHODS[0]:  # "🔍 Search Box"
    st.markdown("### 🔍 Search for Plants")
    
    col1, col2 = st.columns([3, 1])
    
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
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    
    mute_audio = st.checkbox("🔇 Mute Audio", value=True)
    
    if search_button and plant_name:
        try:
            # Check if we have cached data
            if plant_service.get_cached_analysis(plant_name):
                with st.spinner("✨ Loading from cache..."):
                    st.markdown("### 📊 Analysis Results")
                    analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                    st.info("💾 Loaded from cache - instant results!")
            else:
                with st.spinner("🌿 Analyzing plant information..."):
                    st.markdown("### 📊 Analysis Results")
                    analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                    st.success("✅ Analysis complete and cached for future use!")
            
            render_plant_analysis_display(plant_name, analysis, mute_audio)
            
        except Exception as e:
            st.error(f"❌ Error analyzing plant: {str(e)}")

# File Upload Method
elif input_method == config.INPUT_METHODS[1]:  # "📁 File Upload"
    st.markdown("### 📁 Upload Plant Image")
    
    uploaded_image = st.file_uploader(
        "Drop an image or click to browse",
        type=['jpg', 'jpeg', 'png'],
        help="Supported formats: JPG, PNG"
    )
    
    if uploaded_image:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
        
                        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_bytes = uploaded_image.read()
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Check cache status
                if plant_service.get_cached_analysis(plant_name):
                    with st.spinner("✨ Loading from cache..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                        st.info("💾 Loaded from cache - instant results!")
                else:
                    with st.spinner("🌿 Fetching detailed information..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                        st.success("✅ Analysis complete and cached for future use!")
                
                render_plant_analysis_display(plant_name, analysis)
                
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")

# Camera Capture Method
elif input_method == config.INPUT_METHODS[2]:  # "📸 Camera Capture"
    st.markdown("### 📸 Capture Plant Image")
    
    captured_image = st.camera_input("Take a photo of your plant")
    
    if captured_image:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(captured_image, caption='Captured Image', use_column_width=True)
        
        with col2:
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_bytes = captured_image.read()
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✅ Identified: **{plant_name}**")
                
                # Check cache status
                if plant_service.get_cached_analysis(plant_name):
                    with st.spinner("✨ Loading from cache..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                        st.info("💾 Loaded from cache - instant results!")
                else:
                    with st.spinner("🌿 Fetching detailed information..."):
                        analysis = st.write_stream(plant_service.get_analysis_stream(plant_name))
                        st.success("✅ Analysis complete and cached for future use!")
                
                render_plant_analysis_display(plant_name, analysis)
                
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")

# Footer
render_legal_footer()