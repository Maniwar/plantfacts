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


# Footer
render_legal_footer()
# =========================================================
# Compact Responsive Animated GitHub Sponsor Section
# =========================================================

st.markdown("---")

# Compact responsive sponsor section - half height
st.html("""
    <style>
    /* Base animations with reduced motion support */
    @keyframes float-up {
        0% {
            opacity: 0;
            transform: translateY(50px) rotate(0deg);
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            opacity: 0;
            transform: translateY(-50px) rotate(360deg);
        }
    }
    
    @keyframes pulse-glow {
        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }
        50% {
            transform: scale(1.02);
            filter: brightness(1.08);
        }
    }
    
    @keyframes sway {
        0%, 100% {
            transform: translateX(0px);
        }
        50% {
            transform: translateX(15px);
        }
    }
    
    /* Reduced motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        .particle,
        .sparkle,
        .sponsor-content,
        .heart-icon {
            animation: none !important;
        }
    }
    
    /* Main container - compact height */
    .particle-container {
        position: relative;
        width: 100%;
        min-height: 160px;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(102, 187, 106, 0.03) 0%, rgba(102, 126, 234, 0.05) 100%);
        border-radius: 15px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
    }
    
    /* Smaller particles */
    .particle {
        position: absolute;
        font-size: 16px;
        animation: float-up 5s infinite ease-in-out;
        opacity: 0;
        z-index: 1;
        pointer-events: none;
    }
    
    .particle.leaf { animation-delay: 0s; left: 10%; animation-duration: 4s; }
    .particle.flower { animation-delay: 1s; left: 30%; animation-duration: 5s; }
    .particle.sprout { animation-delay: 2s; left: 50%; animation-duration: 4.5s; }
    .particle.seed { animation-delay: 3s; left: 70%; animation-duration: 5.5s; }
    .particle.tree { animation-delay: 4s; left: 90%; animation-duration: 4s; }
    
    .sparkle {
        position: absolute;
        color: #ffd700;
        animation: float-up 3s infinite linear;
        font-size: 12px;
        z-index: 1;
        pointer-events: none;
    }
    
    .sparkle:nth-child(6) { left: 15%; animation-delay: 0.5s; }
    .sparkle:nth-child(7) { left: 85%; animation-delay: 1.5s; }
    .sparkle:nth-child(8) { left: 40%; animation-delay: 2.5s; }
    .sparkle:nth-child(9) { left: 60%; animation-delay: 3.5s; }
    .sparkle:nth-child(10) { left: 25%; animation-delay: 4.5s; }
    
    /* Content box - compact */
    .sponsor-content {
        position: relative;
        text-align: center;
        z-index: 10;
        background: rgba(255, 255, 255, 0.95);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        animation: pulse-glow 3s infinite ease-in-out;
        max-width: 500px;
        width: 90%;
        box-sizing: border-box;
    }
    
    .heart-icon {
        display: inline-block;
        animation: pulse-glow 2s infinite ease-in-out;
        font-size: 1.2rem;
        margin-bottom: 0.25rem;
    }
    
    /* Title - smaller */
    .sponsor-title {
        margin: 0 0 0.25rem 0;
        color: #2d3748;
        font-size: clamp(0.95rem, 3.5vw, 1.2rem);
        font-weight: bold;
    }
    
    /* Subtitle - smaller */
    .sponsor-subtitle {
        margin: 0.25rem 0;
        color: #4a5568;
        font-size: clamp(0.75rem, 2vw, 0.85rem);
    }
    
    /* Button container - compact */
    .button-container {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.5rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    /* Buttons - smaller but still touch-friendly */
    .sponsor-btn {
        display: inline-block;
        padding: 0.5rem 0.75rem;
        min-height: 36px;
        min-width: 70px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        font-size: clamp(0.75rem, 2vw, 0.85rem);
        transition: all 0.3s ease;
        cursor: pointer;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        user-select: none;
        box-sizing: border-box;
        text-align: center;
        line-height: 1.2;
    }
    
    .sponsor-btn.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .sponsor-btn.secondary {
        background: white;
        color: #667eea;
        border: 1.5px solid #667eea;
    }
    
    /* Hover states - desktop only */
    @media (hover: hover) and (pointer: fine) {
        .sponsor-btn.primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
        }
        
        .sponsor-btn.secondary:hover {
            background: #667eea;
            color: white;
            transform: translateY(-1px);
        }
    }
    
    /* Active states for touch devices */
    .sponsor-btn:active {
        transform: scale(0.98);
    }
    
    .sponsor-message {
        color: #667eea;
        font-size: clamp(0.7rem, 1.8vw, 0.75rem);
        font-style: italic;
        margin-top: 0.5rem;
        opacity: 0.9;
        padding: 0 0.25rem;
    }
    
    /* Mobile phones - portrait */
    @media only screen and (max-width: 480px) {
        .particle-container {
            min-height: 140px;
            padding: 0.75rem 0.5rem;
            margin: 0.5rem 0;
            border-radius: 12px;
        }
        
        .sponsor-content {
            padding: 0.75rem;
            width: 95%;
        }
        
        .button-container {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .sponsor-btn {
            width: 100%;
            padding: 0.625rem 0.75rem;
            font-size: 0.85rem;
        }
        
        /* Hide some particles on small screens */
        .particle:nth-child(even),
        .sparkle:nth-child(even) {
            display: none;
        }
    }
    
    /* Mobile phones - landscape */
    @media only screen and (max-width: 812px) and (orientation: landscape) {
        .particle-container {
            min-height: 125px;
            padding: 0.5rem;
        }
        
        .sponsor-content {
            padding: 0.5rem 0.75rem;
        }
        
        .button-container {
            gap: 0.4rem;
        }
        
        .sponsor-btn {
            padding: 0.4rem 0.625rem;
            font-size: 0.75rem;
            min-height: 32px;
        }
    }
    
    /* Tablets */
    @media only screen and (min-width: 481px) and (max-width: 1024px) {
        .particle-container {
            min-height: 150px;
            padding: 1rem;
        }
        
        .sponsor-content {
            padding: 0.875rem 1.25rem;
            max-width: 600px;
        }
        
        .button-container {
            gap: 0.5rem;
        }
        
        .sponsor-btn {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            min-width: 80px;
        }
    }
    
    /* Desktop and larger */
    @media only screen and (min-width: 1025px) {
        .particle-container {
            min-height: 140px;
        }
        
        .sponsor-content {
            padding: 1rem 1.5rem;
        }
        
        .button-container {
            flex-direction: row;
        }
    }
    
    /* iPhone notch safe areas */
    @supports (padding: max(0px)) {
        .particle-container {
            padding-left: max(0.75rem, env(safe-area-inset-left));
            padding-right: max(0.75rem, env(safe-area-inset-right));
        }
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .sponsor-btn {
            border: 2px solid currentColor;
        }
        
        .sponsor-content {
            border: 2px solid #000;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .sponsor-content {
            background: rgba(30, 30, 30, 0.95);
        }
        
        .sponsor-title {
            color: #f0f0f0;
        }
        
        .sponsor-subtitle {
            color: #d0d0d0;
        }
        
        .sponsor-btn.secondary {
            background: #2a2a2a;
            color: #a0a0ff;
            border-color: #a0a0ff;
        }
    }
    
    /* Print styles */
    @media print {
        .particle-container {
            display: none;
        }
    }
    </style>
    
    <div class="particle-container" role="region" aria-label="Support PlantFacts">
        <!-- Floating plant particles -->
        <div class="particle leaf" aria-hidden="true">🍃</div>
        <div class="particle flower" aria-hidden="true">🌸</div>
        <div class="particle sprout" aria-hidden="true">🌱</div>
        <div class="particle seed" aria-hidden="true">🌾</div>
        <div class="particle tree" aria-hidden="true">🌿</div>
        
        <!-- Sparkles -->
        <div class="sparkle" aria-hidden="true">✨</div>
        <div class="sparkle" aria-hidden="true">✨</div>
        <div class="sparkle" aria-hidden="true">✨</div>
        <div class="sparkle" aria-hidden="true">✨</div>
        <div class="sparkle" aria-hidden="true">✨</div>
        
        <!-- All content inside -->
        <div class="sponsor-content">
            <div class="heart-icon" aria-hidden="true">💚</div>
            <h3 class="sponsor-title">Growing PlantFacts Together</h3>
            <p class="sponsor-subtitle">
                Free forever • No ads • Plant-powered
            </p>
            
            <div class="button-container">
                <a href="https://github.com/sponsors/Maniwar" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   class="sponsor-btn primary"
                   aria-label="Support on GitHub Sponsors">
                    🌱 Sponsor
                </a>
                <a href="https://github.com/Maniwar/plantfacts" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   class="sponsor-btn secondary"
                   aria-label="Star PlantFacts on GitHub">
                    ⭐ Star
                </a>
                <a href="https://github.com/Maniwar" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   class="sponsor-btn secondary"
                   aria-label="View all projects on GitHub">
                    🔗 Projects
                </a>
            </div>
            
            <p class="sponsor-message">
                🌿 Your green thumb assistant, always free
            </p>
        </div>
    </div>
""")

st.markdown("---")

