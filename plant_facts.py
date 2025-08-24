"""
Plant Facts Explorer - Clean UI/UX Version
Simplified, user-focused interface with better information hierarchy
Author: Maniwar (UI/UX Improvements)
Version: 6.0.0
"""

import streamlit as st
import base64
import logging
from streamlit_searchbox import st_searchbox

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

# Import utils modules
from utils.config import AppConfig
from utils.cache_service import CacheService
from utils.plant_service import PlantService
from utils.search_service import get_search_suggestions
from utils.ui_components import (
    get_plant_image_info,
    extract_quick_facts,
    render_streaming_content
)

# Initialize configuration
config = AppConfig()

# Page configuration - centered layout for better focus
st.set_page_config(
    layout="centered",  # Changed from wide to centered
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Initialize services
@st.cache_resource
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

# Clean, minimal CSS
st.markdown("""
<style>
    /* Clean, modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean header without animations */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #666;
        font-weight: 400;
    }
    
    /* Method cards */
    .method-card {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .method-card:hover {
        border-color: #059669;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15);
    }
    
    .method-card.selected {
        border-color: #059669;
        background: #f0fdf4;
    }
    
    .method-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .method-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    
    .method-desc {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Search interface */
    .search-container {
        background: #f9fafb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Popular plants - minimal */
    .quick-plants {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .plant-chip {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 0.4rem 1rem;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .plant-chip:hover {
        background: #059669;
        color: white;
        border-color: #059669;
    }
    
    /* Results section */
    .results-container {
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Plant info card */
    .plant-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .plant-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 1rem 1.5rem;
    }
    
    .plant-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .quick-facts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
    }
    
    .fact-item {
        text-align: center;
        padding: 0.75rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .fact-label {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.25rem;
    }
    
    .fact-value {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    /* Clean info display */
    .info-section {
        padding: 1.5rem;
    }
    
    .info-section h3 {
        color: #059669;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    
    /* Loading state */
    .loading-message {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
    
    /* Hide Streamlit's default radio button styling */
    .stRadio > div {
        display: none !important;
    }
    
    /* Success message */
    .cache-badge {
        display: inline-block;
        background: #f0fdf4;
        color: #059669;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    
    /* Reduce default Streamlit spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid #e5e7eb;
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Clean header
st.markdown("""
<div class="main-header">
    <div class="main-title">🌿 Plant Facts Explorer</div>
    <div class="main-subtitle">Get instant AI-powered information about any plant</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for method selection
if 'selected_method' not in st.session_state:
    st.session_state.selected_method = None

# Method selection with visual cards
st.markdown("### Choose how to identify your plant")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍\n\n**Search**\n\nType plant name", key="method_search", use_container_width=True):
        st.session_state.selected_method = "search"

with col2:
    if st.button("📸\n\n**Camera**\n\nTake a photo", key="method_camera", use_container_width=True):
        st.session_state.selected_method = "camera"

with col3:
    if st.button("📁\n\n**Upload**\n\nChoose image", key="method_upload", use_container_width=True):
        st.session_state.selected_method = "upload"

# Main content area based on selection
if st.session_state.selected_method:
    st.markdown("---")
    
    if st.session_state.selected_method == "search":
        st.markdown("### 🔍 Search for a plant")
        
        # Single, clean search interface
        plant_name = st_searchbox(
            search_function=get_search_suggestions,
            placeholder="Type plant name (e.g., Monstera, Rose, Fern)...",
            label=None,
            clear_on_submit=False,
            clearable=True,
            key="plant_searchbox"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Popular suggestions (reduced to 5)
            st.markdown("**Popular:** Rose • Monstera • Snake Plant • Orchid • Aloe Vera")
        with col2:
            search_clicked = st.button("Search 🔍", type="primary", use_container_width=True)
        
        if search_clicked and plant_name:
            process_plant_search(plant_name)
    
    elif st.session_state.selected_method == "camera":
        st.markdown("### 📸 Take a photo")
        
        captured_image = st.camera_input("Point your camera at the plant", label_visibility="collapsed")
        
        if captured_image:
            process_plant_image(captured_image, "Camera capture")
    
    elif st.session_state.selected_method == "upload":
        st.markdown("### 📁 Upload an image")
        
        uploaded_image = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            label_visibility="collapsed"
        )
        
        if uploaded_image:
            process_plant_image(uploaded_image, "Uploaded image")

# Helper functions for processing
def process_plant_search(plant_name):
    """Process plant search and display results"""
    plant_name = plant_name.strip().title()
    
    # Check cache first
    with st.spinner("Searching..."):
        cached_analysis = plant_service.get_cached_analysis(plant_name)
    
    if cached_analysis:
        st.markdown('<div class="cache-badge">✓ Loaded from cache</div>', unsafe_allow_html=True)
        display_plant_info(plant_name, cached_analysis)
    else:
        # Generate new analysis
        st.info("Generating analysis...")
        analysis = ""
        container = st.empty()
        
        for chunk in plant_service.get_analysis_stream(plant_name):
            analysis += chunk
            container.markdown(analysis)
        
        container.empty()
        display_plant_info(plant_name, analysis)

def process_plant_image(image_file, source_type):
    """Process uploaded/captured image"""
    image_bytes = image_file.read()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image_bytes, caption=source_type, use_container_width=True)
    
    with col2:
        with st.spinner("Identifying plant..."):
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            plant_name = plant_service.identify_plant_from_image(image_b64)
            st.success(f"Identified: **{plant_name}**")
    
    # Get analysis
    cached_analysis = plant_service.get_cached_analysis(plant_name)
    
    if cached_analysis:
        st.markdown('<div class="cache-badge">✓ Loaded from cache</div>', unsafe_allow_html=True)
        display_plant_info(plant_name, cached_analysis, image_bytes)
    else:
        st.info("Generating analysis...")
        analysis = ""
        container = st.empty()
        
        for chunk in plant_service.get_analysis_stream(plant_name):
            analysis += chunk
            container.markdown(analysis)
        
        container.empty()
        display_plant_info(plant_name, analysis, image_bytes)

def display_plant_info(plant_name, analysis, user_image=None):
    """Display plant information in a clean, organized way"""
    st.markdown("---")
    st.markdown(f"## 🌱 {plant_name}")
    
    # Image and quick facts side by side
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if user_image:
            st.image(user_image, caption="Your plant", use_container_width=True)
        else:
            img_info = get_plant_image_info(plant_name)
            st.image(img_info["url"], caption=img_info["caption"], use_container_width=True)
    
    with col2:
        st.markdown("### Quick Facts")
        facts = extract_quick_facts(analysis)
        
        if facts:
            for label, value in facts.items():
                st.metric(label=label, value=value)
        else:
            st.info("See detailed information below")
    
    # Detailed information
    st.markdown("### Detailed Information")
    
    # Display analysis in a clean container
    with st.container():
        st.markdown(analysis)

# Minimal footer
st.markdown("---")
st.markdown("""
<div class="app-footer">
    Plant Facts Explorer v6.0 • Powered by AI
    <br>
    <small>For informational purposes only. Always consult experts for professional advice.</small>
</div>
""", unsafe_allow_html=True)