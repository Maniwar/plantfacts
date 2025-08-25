"""
Plant Facts Explorer - Stacked Layout Version
Clean, mobile-first design with everything stacked vertically
Author: Maniwar
Version: 6.0.0 - Simplified stacked layout
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

# Import streamlit_searchbox
from streamlit_searchbox import st_searchbox

# Import utils modules directly
from utils.config import AppConfig
from utils.cache_service import CacheService
from utils.plant_service import PlantService
from utils.search_service import get_search_suggestions
from utils.ui_components import (
    get_plant_image_info,
    extract_quick_facts
)

# Initialize configuration
config = AppConfig()

# Page configuration - centered for better focus
st.set_page_config(
    layout="centered",  # Changed to centered for better stacked layout
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    initial_sidebar_state="collapsed"
)

# Initialize services
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

# Clean CSS for stacked layout
st.markdown("""
<style>
    /* Clean, minimal styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #fafafa;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Simple header */
    .app-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        background: white;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
    }
    
    /* Content cards */
    .content-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Method buttons */
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background: white;
        color: #111827;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #059669;
        color: white;
        border-color: #059669;
    }
    
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) .stButton > button {
        background: #059669;
        color: white;
        border-color: #059669;
    }
    
    /* Results section */
    .results-section {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e5e7eb;
    }
    
    /* Quick facts */
    .quick-fact {
        background: #f9fafb;
        border-left: 3px solid #059669;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
    }
    
    .fact-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.25rem;
    }
    
    .fact-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
    }
    
    /* Images */
    .stImage {
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    /* Reduce spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 700px;
    }
    
    h1, h2, h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Info messages */
    .stAlert {
        margin: 0.5rem 0;
        border-radius: 6px;
    }
    
    /* Search box styling */
    .stTextInput > div > div {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 6px;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
        color: #6b7280;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Simple header
st.markdown("""
<div class="app-header">
    <div class="app-title">🌿 Plant Facts Explorer</div>
    <div class="app-subtitle">Get instant AI-powered information about any plant</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_method' not in st.session_state:
    st.session_state.selected_method = None
if 'do_search' not in st.session_state:
    st.session_state.do_search = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Method selection - stacked buttons
st.markdown("### How would you like to identify your plant?")

# Three stacked method buttons
if st.button("🔍 Search by Name", use_container_width=True):
    st.session_state.selected_method = "search"
    
if st.button("📸 Take a Photo", use_container_width=True):
    st.session_state.selected_method = "camera"
    
if st.button("📁 Upload an Image", use_container_width=True):
    st.session_state.selected_method = "upload"

# Display selected method interface
if st.session_state.selected_method:
    st.markdown("---")
    
    # SEARCH METHOD
    if st.session_state.selected_method == "search":
        st.markdown("### 🔍 Search for a Plant")
        
        # Search box
        plant_name = st_searchbox(
            search_function=get_search_suggestions,
            placeholder="Type plant name (e.g., Rose, Monstera, Fern)...",
            label=None,
            clear_on_submit=False,
            clearable=True,
            key="plant_searchbox"
        )
        
        # Search button
        if st.button("Search", type="primary", use_container_width=True):
            if plant_name:
                st.session_state.search_query = plant_name
                st.session_state.do_search = True
        
        # Quick suggestions
        st.markdown("**Popular searches:** Rose • Monstera • Snake Plant • Orchid • Aloe Vera")
        
        # Audio option
        mute_audio = st.checkbox("🔇 Mute Audio", value=True, key="mute_search")
        
        # Execute search
        if st.session_state.do_search and st.session_state.search_query:
            st.session_state.do_search = False
            search_term = st.session_state.search_query
            
            try:
                plant_name = search_term.strip().title()
                
                if not plant_name:
                    st.warning("Please enter a plant name to search.")
                else:
                    # Show loading
                    with st.spinner("🌿 Getting plant information..."):
                        # Check cache first
                        cached_analysis = plant_service.get_cached_analysis(plant_name)
                        
                        if cached_analysis:
                            analysis = cached_analysis
                            st.success("✓ Found in cache - instant results!")
                        else:
                            # Generate new analysis
                            analysis = ""
                            placeholder = st.empty()
                            
                            for chunk in plant_service.get_analysis_stream(plant_name):
                                analysis += chunk
                                placeholder.markdown(analysis)
                            
                            placeholder.empty()
                            st.success("✓ Analysis complete!")
                    
                    # Display results in stacked layout
                    display_plant_results(plant_name, analysis, mute_audio)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # CAMERA METHOD
    elif st.session_state.selected_method == "camera":
        st.markdown("### 📸 Take a Photo")
        
        captured_image = st.camera_input("Point your camera at the plant", label_visibility="collapsed")
        mute_audio = st.checkbox("🔇 Mute Audio", value=True, key="mute_camera")
        
        if captured_image:
            # Process image
            image_bytes = captured_image.read()
            
            # Display image
            st.image(image_bytes, caption="Your photo", use_container_width=True)
            
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✓ Identified: **{plant_name}**")
                
                # Get analysis
                with st.spinner("🌿 Getting plant information..."):
                    cached_analysis = plant_service.get_cached_analysis(plant_name)
                    
                    if cached_analysis:
                        analysis = cached_analysis
                        st.info("✓ Found in cache!")
                    else:
                        # Generate new
                        analysis = ""
                        placeholder = st.empty()
                        
                        for chunk in plant_service.get_analysis_stream(plant_name):
                            analysis += chunk
                            placeholder.markdown(analysis)
                        
                        placeholder.empty()
                        st.success("✓ Analysis complete!")
                
                # Display results
                display_plant_results(plant_name, analysis, mute_audio, image_bytes)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # UPLOAD METHOD
    elif st.session_state.selected_method == "upload":
        st.markdown("### 📁 Upload an Image")
        
        uploaded_image = st.file_uploader(
            "Choose a plant image",
            type=['jpg', 'jpeg', 'png'],
            label_visibility="collapsed"
        )
        mute_audio = st.checkbox("🔇 Mute Audio", value=True, key="mute_upload")
        
        if uploaded_image:
            # Process image
            image_bytes = uploaded_image.read()
            
            # Display image
            st.image(image_bytes, caption="Your image", use_container_width=True)
            
            try:
                with st.spinner("🤖 Identifying plant..."):
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    plant_name = plant_service.identify_plant_from_image(image_b64)
                    st.success(f"✓ Identified: **{plant_name}**")
                
                # Get analysis
                with st.spinner("🌿 Getting plant information..."):
                    cached_analysis = plant_service.get_cached_analysis(plant_name)
                    
                    if cached_analysis:
                        analysis = cached_analysis
                        st.info("✓ Found in cache!")
                    else:
                        # Generate new
                        analysis = ""
                        placeholder = st.empty()
                        
                        for chunk in plant_service.get_analysis_stream(plant_name):
                            analysis += chunk
                            placeholder.markdown(analysis)
                        
                        placeholder.empty()
                        st.success("✓ Analysis complete!")
                
                # Display results
                display_plant_results(plant_name, analysis, mute_audio, image_bytes)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Helper function to display results in stacked layout
def display_plant_results(plant_name, analysis, mute_audio=True, user_image=None):
    """Display plant information in a clean stacked layout"""
    
    st.markdown("---")
    st.markdown(f"## 🌱 {plant_name}")
    
    # Display image (either user's or fetched)
    if user_image:
        st.image(user_image, caption=f"{plant_name} - Your image", use_container_width=True)
    else:
        img_info = get_plant_image_info(plant_name)
        caption = f"{plant_name}"
        if img_info.get("caption"):
            caption += f" - {img_info['caption']}"
        st.image(img_info["url"], caption=caption, use_container_width=True)
    
    # Quick facts
    st.markdown("### Quick Facts")
    facts = extract_quick_facts(analysis)
    
    if facts:
        for label, value in facts.items():
            st.markdown(f"""
            <div class="quick-fact">
                <div class="fact-label">{label}</div>
                <div class="fact-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("See detailed information below")
    
    # Audio player (if enabled)
    if not mute_audio:
        st.markdown("### 🔊 Audio Guide")
        try:
            from gtts import gTTS
            from io import BytesIO
            import re
            
            # Clean text for TTS
            clean_text = re.sub(r'\*\*|\#\#|\#|\*|\[.*?\]\(.*?\)', '', analysis)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Generate audio
            audio_stream = BytesIO()
            tts = gTTS(text=clean_text[:5000], lang='en')  # Limit to 5000 chars
            tts.write_to_fp(audio_stream)
            st.audio(audio_stream, format="audio/mpeg")
        except Exception as e:
            st.warning("Audio generation unavailable")
    
    # Detailed information
    st.markdown("### Detailed Information")
    with st.container():
        st.markdown(analysis)

# System status (hidden in expander at bottom)
st.markdown("---")
with st.expander("⚙️ System Status"):
    # Cache status
    if cache_service.is_connected():
        st.success("✅ Cache: Connected")
    else:
        st.info("ℹ️ Cache: Not configured (app works without caching)")
    
    # Version info
    st.info(f"Version: {config.APP_VERSION} | Author: {config.AUTHOR}")
    
    # Cache check tool
    if cache_service.is_connected():
        test_plant = st.text_input("Check if plant is cached:", placeholder="e.g., Rose")
        if test_plant:
            test_plant_normalized = test_plant.strip().title()
            if plant_service.get_cached_analysis(test_plant_normalized):
                st.success(f"✅ '{test_plant_normalized}' is in cache")
            else:
                st.info(f"❌ '{test_plant_normalized}' not cached yet")

# Simple footer
st.markdown("""
<div class="app-footer">
    Plant Facts Explorer • AI-Powered Plant Guide
    <br>
    <small>For informational purposes only. Consult experts for professional advice.</small>
</div>
""", unsafe_allow_html=True)