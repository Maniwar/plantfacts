"""
Plant Facts Explorer - Main Application
A modular Streamlit app for plant identification and information
Author: Maniwar
Version: 5.1.0 - Enhanced search with Enter key support and auto-search on selection
"""

import streamlit as st
import base64
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

# Global setting for particles (easily toggle on/off)
ENABLE_PARTICLES = False  # Set to True to enable subtle particle effects

# Import streamlit_searchbox
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
    render_legal_footer,
    render_streaming_content
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

# Apply minimal custom CSS
render_custom_css()

# Render header
render_header()



# Input method selector with modern styling
with st.container():
    st.subheader("🎯 Choose Your Input Method")
    input_method = st.radio(
        "Select how you want to identify your plant:",
        config.INPUT_METHODS,
        horizontal=True,
        label_visibility="collapsed"
    )

# Search Box Method - Unified solution with Enter key support
if input_method == config.INPUT_METHODS[0]:  # "🔍 Search Box"
    with st.container(border=True):
        st.subheader("🔍 Search for Plants")
        
        # Initialize session state
        if 'do_search' not in st.session_state:
            st.session_state.do_search = False
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        
        # Main search interface
        col1, col2 = st.columns([4, 1], gap="medium")
        
        with col1:
            # Define callback for searchbox selection
            def handle_selection(selected_value):
                """Automatically trigger search when item is selected from dropdown"""
                if selected_value:
                    st.session_state.search_query = selected_value
                    st.session_state.do_search = True
            
            # Searchbox with automatic search on selection
            plant_name = st_searchbox(
                search_function=get_search_suggestions,
                placeholder="Type plant name...",
                label=None,
                clear_on_submit=False,
                clearable=True,
                key="plant_searchbox",
                submit_function=handle_selection  # Auto-search on selection
            )
        
        with col2:
            # Search button for typed text (without selection)
            if st.button("🔍 Search", type="primary", use_container_width=True):
                if plant_name:
                    st.session_state.search_query = plant_name
                    st.session_state.do_search = True
        
        # For mobile/Enter key support: Simple text input as fallback
        with st.container():
            st.caption("💡 Type into drop down above & pick from the the list to search.")
            
        #     # Form captures Enter key
        #     with st.form(key="text_search_form", clear_on_submit=False):
        #         cols = st.columns([5, 1])
        #         with cols[0]:
        #             text_input = st.text_input(
        #                 "Direct input",
        #                 placeholder="Type any plant name and press Enter...",
        #                 label_visibility="collapsed",
        #                 value=plant_name if plant_name else ""  # Mirror searchbox value
        #             )
        #         with cols[1]:
        #             if st.form_submit_button("Go →", use_container_width=True):
        #                 if text_input:
        #                     st.session_state.search_query = text_input
        #                     st.session_state.do_search = True
        
        # # Quick search buttons for popular plants
        # st.divider()
        # st.caption("🌿 **Popular plants** - tap to search instantly:")
        
        # # Two rows of quick buttons
        # row1_cols = st.columns(5)
        # popular_plants_row1 = ["Rose", "Monstera", "Snake Plant", "Orchid", "Fern"]
        # for idx, plant in enumerate(popular_plants_row1):
        #     with row1_cols[idx]:
        #         if st.button(plant, key=f"pop_{plant}", use_container_width=True):
        #             st.session_state.search_query = plant
        #             st.session_state.do_search = True
        
        # row2_cols = st.columns(5)
        # popular_plants_row2 = ["Cactus", "Aloe Vera", "Pothos", "Peace Lily", "Bamboo"]
        # for idx, plant in enumerate(popular_plants_row2):
        #     with row2_cols[idx]:
        #         if st.button(plant, key=f"pop2_{plant}", use_container_width=True, type="secondary"):
        #             st.session_state.search_query = plant
        #             st.session_state.do_search = True
        
        st.divider()
        mute_audio = st.checkbox("🔇 Mute Audio", value=True)
    
    # Execute search when triggered
    if st.session_state.do_search and st.session_state.search_query:
        # Reset the trigger
        st.session_state.do_search = False
        search_term = st.session_state.search_query
        
        try:
            # Normalize plant name for consistent caching
            plant_name = search_term.strip().title()
            
            if not plant_name:
                st.warning("Please enter a plant name to search.")
            else:
                # Create a placeholder for the content
                content_placeholder = st.empty()
                
                # Check cache first
                cached_analysis = plant_service.get_cached_analysis(plant_name)
                
                if cached_analysis:
                    # Display cached content instantly
                    if cache_service.is_connected():
                        st.info("💾 Loading from cache - instant results!")
                    analysis = cached_analysis
                else:
                    # Stream new content
                    st.info("🌿 Generating new analysis...")
                    
                    with content_placeholder.container():
                        st.markdown("### 🔍 Live Analysis Stream")
                        analysis = ""
                        stream_container = st.empty()
                        
                        for chunk in plant_service.get_analysis_stream(plant_name):
                            analysis += chunk
                            render_streaming_content(analysis, stream_container)
                    
                    content_placeholder.empty()
                    if cache_service.is_connected():
                        st.success("✅ Analysis complete and cached for future use!")
                    else:
                        st.success("✅ Analysis complete!")
                
                # Display the formatted analysis
                st.divider()
                render_plant_analysis_display(plant_name, analysis, mute_audio, particles=ENABLE_PARTICLES)
                
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
            st.image(image_bytes, caption='Uploaded Image', width='stretch')
        
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
                            render_streaming_content(analysis, stream_container)
                    
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
                particles=ENABLE_PARTICLES,
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
            st.image(image_bytes, caption='Captured Image', width='stretch')
        
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
                            render_streaming_content(analysis, stream_container)
                    
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
                particles=ENABLE_PARTICLES,
                uploaded_image_bytes=image_bytes  # Pass the captured image
            )
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
                else:
                    st.info(f"❌ '{test_plant_normalized}' not cached yet")


# =========================================================
# Animated GitHub Sponsor Section with Plant Particles
# =========================================================

st.markdown("---")

# Animated sponsor section with floating plant particles
st.html("""
    <style>
    @keyframes float-up {
        0% {
            opacity: 0;
            transform: translateY(100px) rotate(0deg);
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            opacity: 0;
            transform: translateY(-100px) rotate(360deg);
        }
    }
    
    @keyframes pulse-glow {
        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }
        50% {
            transform: scale(1.05);
            filter: brightness(1.2);
        }
    }
    
    @keyframes sway {
        0%, 100% {
            transform: translateX(0px);
        }
        50% {
            transform: translateX(30px);
        }
    }
    
    .particle-container {
        position: relative;
        width: 100%;
        height: 200px;
        overflow: hidden;
        background: linear-gradient(180deg, transparent 0%, rgba(102, 126, 234, 0.05) 100%);
        border-radius: 20px;
        margin: 2rem 0;
    }
    
    .particle {
        position: absolute;
        font-size: 20px;
        animation: float-up 6s infinite ease-in-out;
        opacity: 0;
    }
    
    .particle.leaf { animation-delay: 0s; left: 10%; animation-duration: 5s; }
    .particle.flower { animation-delay: 1s; left: 30%; animation-duration: 6s; }
    .particle.sprout { animation-delay: 2s; left: 50%; animation-duration: 5.5s; }
    .particle.seed { animation-delay: 3s; left: 70%; animation-duration: 6.5s; }
    .particle.tree { animation-delay: 4s; left: 90%; animation-duration: 5s; }
    
    .particle:nth-child(odd) {
        animation-name: float-up, sway;
        animation-duration: 6s, 3s;
        animation-iteration-count: infinite;
    }
    
    .sponsor-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: pulse-glow 3s infinite ease-in-out;
    }
    
    .heart-icon {
        display: inline-block;
        animation: pulse-glow 2s infinite ease-in-out;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sparkle {
        position: absolute;
        color: #ffd700;
        animation: float-up 3s infinite linear;
        font-size: 14px;
    }
    
    .sparkle:nth-child(6) { left: 15%; animation-delay: 0.5s; }
    .sparkle:nth-child(7) { left: 85%; animation-delay: 1.5s; }
    .sparkle:nth-child(8) { left: 40%; animation-delay: 2.5s; }
    .sparkle:nth-child(9) { left: 60%; animation-delay: 3.5s; }
    .sparkle:nth-child(10) { left: 25%; animation-delay: 4.5s; }
    </style>
    
    <div class="particle-container">
        <!-- Floating plant particles -->
        <div class="particle leaf">🍃</div>
        <div class="particle flower">🌸</div>
        <div class="particle sprout">🌱</div>
        <div class="particle seed">🌾</div>
        <div class="particle tree">🌿</div>
        
        <!-- Sparkles for extra magic -->
        <div class="sparkle">✨</div>
        <div class="sparkle">✨</div>
        <div class="sparkle">✨</div>
        <div class="sparkle">✨</div>
        <div class="sparkle">✨</div>
        
        <!-- Main content -->
        <div class="sponsor-content">
            <div class="heart-icon">💚</div>
            <h3 style="margin: 0 0 0.5rem 0; color: #2d3748;">Growing PlantFacts Together</h3>
            <p style="margin: 0.5rem 0; color: #4a5568; font-size: 0.9rem;">
                Free forever • No ads • Plant-powered
            </p>
        </div>
    </div>
""")

# Sponsor buttons with animation on hover
col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])

with col2:
    if st.button("🌱 Sponsor", key="sponsor_animated", use_container_width=True, type="primary"):
        st.balloons()
        st.html("""
            <script>
            window.open('https://github.com/sponsors/Maniwar', '_blank');
            </script>
        """)

with col3:
    if st.button("⭐ Star Repo", key="star_animated", use_container_width=True):
        st.html("""
            <script>
            window.open('https://github.com/Maniwar/plantfacts', '_blank');
            </script>
        """)
        
with col4:
    if st.button("🔗 All Projects", key="projects_animated", use_container_width=True):
        st.html("""
            <script>
            window.open('https://github.com/Maniwar', '_blank');
            </script>
        """)

# Fun animated message that changes
plant_messages = [
    "🌿 Every plant deserves to live its best life",
    "🌱 Keeping plants alive, one search at a time",
    "🍃 Your green thumb assistant, always free",
    "🌸 Plants make people happy. This app helps.",
    "🌾 Built by a plant parent, for plant parents"
]

import random
import time

# Use time-based selection for variety
message_index = int(time.time() / 10) % len(plant_messages)

st.html(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <p style="
            color: #667eea;
            font-size: 0.9rem;
            font-style: italic;
            opacity: 0;
            animation: fadeIn 2s forwards;
        ">
            {plant_messages[message_index]}
        </p>
    </div>
    
    <style>
    @keyframes fadeIn {{
        to {{ opacity: 1; }}
    }}
    </style>
""")

# Optional: Confetti burst on special occasions
if random.random() < 0.1:  # 10% chance to show special effect
    st.html("""
        <script>
        // Create falling leaves effect
        function createLeaves() {
            const leaves = ['🍃', '🌿', '🍀', '🌱'];
            for (let i = 0; i < 15; i++) {
                setTimeout(() => {
                    const leaf = document.createElement('div');
                    leaf.innerHTML = leaves[Math.floor(Math.random() * leaves.length)];
                    leaf.style.position = 'fixed';
                    leaf.style.left = Math.random() * 100 + '%';
                    leaf.style.top = '-50px';
                    leaf.style.fontSize = (Math.random() * 20 + 15) + 'px';
                    leaf.style.opacity = '0.8';
                    leaf.style.pointerEvents = 'none';
                    leaf.style.zIndex = '9999';
                    leaf.style.transition = 'all 4s ease-in-out';
                    leaf.style.transform = 'rotate(0deg)';
                    
                    document.body.appendChild(leaf);
                    
                    setTimeout(() => {
                        leaf.style.top = '100%';
                        leaf.style.transform = 'rotate(360deg)';
                        leaf.style.opacity = '0';
                    }, 100);
                    
                    setTimeout(() => leaf.remove(), 4100);
                }, i * 200);
            }
        }
        
        // Trigger on page load with delay
        setTimeout(createLeaves, 1000);
        </script>
    """)

st.markdown("---")

# Footer
render_legal_footer()