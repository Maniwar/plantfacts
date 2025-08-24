"""
UI Components Module
Reusable UI components using Streamlit 2025 features and proper CSS implementation
Author: Maniwar
"""

import streamlit as st
import re
from gtts import gTTS
from io import BytesIO
from typing import Dict, Optional

def load_custom_css():
    """
    Load custom CSS that actually works with Streamlit
    Uses st.markdown with unsafe_allow_html=True for proper CSS injection
    """
    css = """
    <style>
        /* Import Google Fonts and FontAwesome */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        
        /* Global App Styling */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header with floating leaf animation */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header-content {
            display: flex;
            align-items: center;
            color: white;
        }
        
        .header-icon {
            font-size: 60px;
            margin-right: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .header-text h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: white !important;
            background: none !important;
            -webkit-text-fill-color: white !important;
        }
        
        .header-text p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.95;
            color: white;
        }
        
        /* Style containers with borders */
        div[data-testid="stContainer"] > div:has(> div[data-testid="stVerticalBlock"]) {
            background: rgba(255, 255, 255, 0.95);
            transition: all 0.3s ease;
        }
        
        /* Style metrics containers */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border: 1px solid #667eea30;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }
        
        /* Style metric labels and values */
        [data-testid="metric-container"] label {
            color: #667eea;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Success, info, warning boxes */
        .stSuccess, .stInfo, .stWarning {
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .stSuccess {
            background: #d4edda;
            border-left-color: #28a745;
        }
        
        .stInfo {
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }
        
        .stWarning {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Container with border styling */
        div.stContainer[data-container-border="true"] {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Radio button styling */
        .stRadio > div {
            display: flex;
            gap: 1rem;
        }
        
        /* Image container styling */
        .stImage {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Divider styling */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #e2e8f0;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .header-text h1 {
                font-size: 1.8rem;
            }
            .header-icon {
                font-size: 40px;
            }
            .header-container {
                padding: 1.5rem;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header():
    """
    Render the application header with floating leaf animation
    """
    # Create header with gradient background and floating leaf
    header_html = """
    <div class="header-container">
        <div class="header-content">
            <div class="header-icon">
                <i class="fas fa-leaf"></i>
            </div>
            <div class="header-text">
                <h1>Plant Facts Explorer</h1>
                <p>Discover detailed information about any plant with AI-powered insights</p>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.divider()

def get_plant_image(plant_name: str) -> str:
    """
    Get a plant image URL from Unsplash
    
    Args:
        plant_name: Name of the plant
        
    Returns:
        Image URL
    """
    # Import config here to avoid circular imports
    from utils.config import AppConfig
    config = AppConfig()
    
    return f"https://source.unsplash.com/{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}/?{plant_name.replace(' ', ',')},plant,nature"

def extract_quick_facts(analysis: str) -> Dict[str, str]:
    """
    Extract quick facts from plant analysis
    """
    # Import config here to avoid circular imports
    from utils.config import AppConfig
    config = AppConfig()
    
    facts = {}
    
    # Toxicity check
    analysis_lower = analysis.lower()
    if "toxic" in analysis_lower:
        if "not toxic" in analysis_lower or "non-toxic" in analysis_lower:
            facts["Toxicity"] = "Safe ✅"
        else:
            facts["Toxicity"] = "Toxic ⚠️"
    
    # Light requirements
    for pattern in config.LIGHT_PATTERNS:
        if pattern in analysis_lower:
            facts["Light"] = pattern.title()
            break
    
    # Watering needs
    for pattern, value in config.WATER_PATTERNS.items():
        if pattern in analysis_lower:
            facts["Water"] = value
            break
    
    # Origin
    origin_match = re.search(r'native to ([^,\.]+)', analysis_lower)
    if origin_match:
        facts["Origin"] = origin_match.group(1).title()
    
    return facts

def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech conversion
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\#\#(.*?)\n', r'\1. ', text)  # Convert headers
    text = re.sub(r'\#(.*?)\n', r'\1. ', text)
    text = re.sub(r'\* (.*?)\n', r'\1. ', text)  # Convert list items
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links
    text = text.replace('|', ', ').replace('-', ' ').replace('`', '')
    return text

def render_plant_analysis_display(plant_name: str, analysis: str, mute_audio: bool = True):
    """
    Render plant analysis using Streamlit 2025 features
    """
    # Main header with gradient effect
    st.markdown(f"## 🌱 Analysis: {plant_name}")
    
    # Create responsive columns with borders
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Plant image with rounded corners (via CSS)
        image_url = get_plant_image(plant_name)
        st.image(image_url, caption=plant_name, use_container_width=True)
        
        # Quick Facts section with modern metrics
        with st.container(border=True):
            st.markdown("### ⭐ Quick Facts")
            facts = extract_quick_facts(analysis)
            
            if facts:
                # Create a 2-column grid for metrics
                metric_cols = st.columns(2)
                for i, (label, value) in enumerate(facts.items()):
                    with metric_cols[i % 2]:
                        st.metric(label=label, value=value)
            else:
                st.info("Analyzing plant characteristics...")
        
        # Audio section
        if not mute_audio:
            with st.container(border=True):
                st.markdown("### 🔊 Audio Guide")
                with st.spinner("Generating audio narration..."):
                    try:
                        clean_analysis = clean_text_for_tts(analysis)
                        audio_stream = BytesIO()
                        tts = gTTS(text=clean_analysis, lang='en')
                        tts.write_to_fp(audio_stream)
                        st.audio(audio_stream, format="audio/mpeg")
                    except Exception as e:
                        st.warning(f"Audio generation unavailable: {str(e)}")
    
    with col2:
        # Create scrollable container for detailed analysis (new 2025 feature)
        with st.container(height=600):
            st.markdown("### 📋 Detailed Analysis")
            
            # Parse and display sections
            sections = analysis.split('\n\n')
            
            for section in sections:
                if section.strip():
                    section_lower = section.lower()
                    
                    # General Information
                    if any(x in section_lower for x in ["general information", "**1."]):
                        with st.container(border=True):
                            st.markdown("#### 📝 General Information")
                            content = re.sub(r'\*\*(?:1\.|General Information:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    # Care Instructions
                    elif any(x in section_lower for x in ["care instructions", "**2."]):
                        with st.container(border=True):
                            st.markdown("#### 🌱 Care Instructions")
                            content = re.sub(r'\*\*(?:2\.|Care Instructions:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    # Toxicity
                    elif any(x in section_lower for x in ["toxicity", "**3."]):
                        container_type = st.warning if "toxic" in section_lower and "not toxic" not in section_lower else st.container
                        if container_type == st.warning:
                            st.warning("⚠️ **Toxicity Warning**\n\n" + re.sub(r'\*\*(?:3\.|Toxicity:?)\*\*:?\s*', '', section))
                        else:
                            with st.container(border=True):
                                st.markdown("#### ⚠️ Toxicity Information")
                                content = re.sub(r'\*\*(?:3\.|Toxicity:?)\*\*:?\s*', '', section)
                                st.markdown(content)
                    
                    # Propagation
                    elif any(x in section_lower for x in ["propagation", "**4."]):
                        with st.container(border=True):
                            st.markdown("#### 🌿 Propagation Methods")
                            content = re.sub(r'\*\*(?:4\.|Propagation:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    # Common Issues
                    elif any(x in section_lower for x in ["common issues", "problems", "**5."]):
                        with st.expander("🐛 Common Issues & Solutions", expanded=True):
                            content = re.sub(r'\*\*(?:5\.|Common Issues:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    # Interesting Facts
                    elif any(x in section_lower for x in ["interesting facts", "**6."]):
                        with st.container(border=True):
                            st.markdown("#### 💡 Interesting Facts")
                            content = re.sub(r'\*\*(?:6\.|Interesting Facts:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    # Other sections
                    else:
                        if section.strip():
                            with st.container(border=True):
                                st.markdown(section)

def render_custom_css():
    """Apply custom CSS styles to the app"""
    load_custom_css()

def render_legal_footer():
    """Render the legal disclaimer and footer"""
    st.divider()
    
    with st.expander("📜 Legal and Data Privacy Statement"):
        legal_container = st.container()
        with legal_container:
            st.markdown("""
            ### Legal Statement
            This application is provided "as is" without any warranties, express or implied. 
            The information provided is for informational purposes only and not a substitute 
            for professional advice regarding plant care or safety.
            
            ### Data Privacy
            - **Collection**: Only plant queries are collected for service provision
            - **Usage**: Data is cached temporarily for performance optimization
            - **Sharing**: No third-party data sharing except OpenAI for analysis
            - **Security**: Standard security measures implemented
            
            ### Copyright
            © 2024 Plant Facts Explorer by Maniwar. Licensed under MIT License.
            
            *AI-generated content should be verified with professional sources.*
            """)
    
    # Footer with author credit
    footer_container = st.container()
    with footer_container:
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem; margin-top: 2rem; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 12px; color: white;'>
                <p style='margin: 0; font-size: 1.1rem;'>🌿 Plant Facts Explorer</p>
                <p style='margin: 0.5rem 0; opacity: 0.9;'>Created with ❤️ by Maniwar</p>
                <p style='margin: 0; opacity: 0.8; font-size: 0.9rem;'>© 2024 | MIT License</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
