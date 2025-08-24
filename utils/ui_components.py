"""
UI Components Module
Reusable UI components with beautiful, modern design
Author: Maniwar
Version: 2.3.0 - Beautiful UI redesign
"""

import streamlit as st
import re
from gtts import gTTS
from io import BytesIO
from typing import Dict, Optional

def load_custom_css():
    """
    Load custom CSS for beautiful, modern UI
    """
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');
        
        /* Hide weird 0 and comment elements */
        .stMarkdown p:empty,
        span:empty,
        div[data-testid="stMarkdownContainer"] > p:empty {
            display: none !important;
        }
        
        /* Global App Styling */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Beautiful Header */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        
        .header-container::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 60%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(20px); }
        }
        
        .header-content {
            display: flex;
            align-items: center;
            color: white;
            position: relative;
            z-index: 1;
        }
        
        .header-icon {
            font-size: 72px;
            margin-right: 24px;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(5deg); }
        }
        
        .header-text h1 {
            margin: 0;
            font-size: 3rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header-text p {
            margin: 0.75rem 0 0 0;
            font-size: 1.25rem;
            opacity: 0.95;
            color: rgba(255,255,255,0.95);
            font-weight: 400;
        }
        
        /* Analysis Container Styling */
        .analysis-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 16px 16px 0 0;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* Metrics Styling */
        [data-testid="metric-container"] {
            background: white;
            border: 2px solid #e2e8f0;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
            border-color: #667eea;
        }
        
        [data-testid="metric-container"] label {
            color: #64748b;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 1.75rem;
            font-weight: 700;
            color: #1e293b;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Container with border */
        div[data-testid="stContainer"][data-container-border="true"],
        .stContainer > div:has(> div[data-testid="stVerticalBlock"]) {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        /* Success/Info/Warning Messages */
        .stSuccess, .stInfo, .stWarning {
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: none;
            font-weight: 500;
        }
        
        .stSuccess {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        
        .stInfo {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }
        
        /* Radio buttons */
        .stRadio > div[role="radiogroup"] {
            background: white;
            padding: 0.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 12px;
            font-weight: 600;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: #f8fafc;
        }
        
        /* Images */
        .stImage {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        
        /* Divider */
        hr {
            margin: 3rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }
        
        /* Scrollable container */
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            gap: 1rem;
        }
        
        /* Hide empty paragraphs and zeros */
        p:empty,
        span:contains("0"):only-child,
        .element-container:has(> div > p:empty) {
            display: none !important;
        }
        
        /* Footer */
        .footer-container {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 3rem;
            border-radius: 24px;
            margin-top: 4rem;
            color: white;
            text-align: center;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .header-text h1 {
                font-size: 2rem;
            }
            .header-icon {
                font-size: 48px;
            }
            .header-container {
                padding: 2rem 1.5rem;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header():
    """
    Render beautiful application header
    """
    header_html = """
    <div class="header-container">
        <div class="header-content">
            <div class="header-icon">
                🌿
            </div>
            <div class="header-text">
                <h1>Plant Facts Explorer</h1>
                <p>Discover the amazing world of plants with AI-powered insights</p>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def get_plant_image(plant_name: str) -> str:
    """
    Get a plant image URL from Unsplash
    """
    from utils.config import AppConfig
    config = AppConfig()
    return f"https://source.unsplash.com/{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}/?{plant_name.replace(' ', ',')},plant,botanical,garden"

def extract_quick_facts(analysis: str) -> Dict[str, str]:
    """
    Extract quick facts from plant analysis
    """
    from utils.config import AppConfig
    config = AppConfig()
    
    facts = {}
    analysis_lower = analysis.lower()
    
    # Toxicity check with better icons
    if "toxic" in analysis_lower:
        if "not toxic" in analysis_lower or "non-toxic" in analysis_lower:
            facts["Safety"] = "Pet Safe ✅"
        else:
            facts["Safety"] = "Toxic ⚠️"
    
    # Light requirements with icons
    light_icons = {
        "full sun": "☀️ Full Sun",
        "partial shade": "⛅ Partial",
        "full shade": "🌙 Shade",
        "bright indirect": "💡 Bright",
        "low light": "🔅 Low Light"
    }
    
    for pattern, display in light_icons.items():
        if pattern in analysis_lower:
            facts["Light"] = display
            break
    
    # Watering with icons
    water_icons = {
        "daily": "💧 Daily",
        "weekly": "💦 Weekly",
        "moderate": "💧 Moderate",
        "drought": "🌵 Minimal"
    }
    
    for pattern, display in water_icons.items():
        if pattern in analysis_lower:
            facts["Water"] = display
            break
    
    # Origin with flag emoji (simplified)
    origin_match = re.search(r'native to ([^,\.]+)', analysis_lower)
    if origin_match:
        origin = origin_match.group(1).title()
        facts["Origin"] = f"🌍 {origin}"
    
    return facts

def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech conversion
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\#\#(.*?)\n', r'\1. ', text)
    text = re.sub(r'\#(.*?)\n', r'\1. ', text)
    text = re.sub(r'\* (.*?)\n', r'\1. ', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = text.replace('|', ', ').replace('-', ' ').replace('`', '')
    return text

def render_plant_analysis_display(plant_name: str, analysis: str, mute_audio: bool = True):
    """
    Render beautiful plant analysis display
    """
    # Main container with nice styling
    with st.container():
        # Beautiful header for analysis
        st.markdown(f"""
        <div class="analysis-header">
            <span>🌱</span>
            <span>Analysis: {plant_name}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Create responsive columns
        col1, col2 = st.columns([2, 3], gap="large")
        
        with col1:
            # Plant image with nice styling
            image_url = get_plant_image(plant_name)
            st.image(image_url, caption=f"🌿 {plant_name}", use_container_width=True)
            
            # Quick Facts with beautiful cards
            st.markdown("### ⭐ Quick Facts")
            facts = extract_quick_facts(analysis)
            
            if facts:
                # Create a 2-column grid for metrics
                fact_cols = st.columns(2)
                for i, (label, value) in enumerate(facts.items()):
                    with fact_cols[i % 2]:
                        # Use container for better styling
                        with st.container():
                            st.metric(label=label, value=value)
            
            # Audio section (if not muted)
            if not mute_audio:
                st.markdown("### 🔊 Audio Guide")
                with st.spinner("Generating audio..."):
                    try:
                        clean_analysis = clean_text_for_tts(analysis)
                        audio_stream = BytesIO()
                        tts = gTTS(text=clean_analysis, lang='en')
                        tts.write_to_fp(audio_stream)
                        st.audio(audio_stream, format="audio/mpeg")
                    except Exception as e:
                        st.warning(f"Audio unavailable: {str(e)}")
        
        with col2:
            # Detailed analysis with scrollable container
            st.markdown("### 📋 Detailed Information")
            
            # Parse and display sections beautifully
            sections = analysis.split('\n\n')
            
            for section in sections:
                if section.strip():
                    section_lower = section.lower()
                    
                    # Format each section type differently
                    if any(x in section_lower for x in ["general information", "**1."]):
                        with st.expander("📝 General Information", expanded=True):
                            content = re.sub(r'\*\*(?:1\.|General Information:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    elif any(x in section_lower for x in ["care instructions", "**2."]):
                        with st.expander("🌱 Care Instructions", expanded=True):
                            content = re.sub(r'\*\*(?:2\.|Care Instructions:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    elif any(x in section_lower for x in ["toxicity", "**3."]):
                        is_toxic = "toxic" in section_lower and "not toxic" not in section_lower
                        with st.expander("⚠️ Safety Information", expanded=is_toxic):
                            content = re.sub(r'\*\*(?:3\.|Toxicity:?)\*\*:?\s*', '', section)
                            if is_toxic:
                                st.warning(content)
                            else:
                                st.success(content)
                    
                    elif any(x in section_lower for x in ["propagation", "**4."]):
                        with st.expander("🌿 Propagation Methods", expanded=False):
                            content = re.sub(r'\*\*(?:4\.|Propagation:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    elif any(x in section_lower for x in ["common issues", "problems", "**5."]):
                        with st.expander("🐛 Common Issues & Solutions", expanded=False):
                            content = re.sub(r'\*\*(?:5\.|Common Issues:?)\*\*:?\s*', '', section)
                            st.markdown(content)
                    
                    elif any(x in section_lower for x in ["interesting facts", "**6."]):
                        with st.expander("💡 Interesting Facts", expanded=True):
                            content = re.sub(r'\*\*(?:6\.|Interesting Facts:?)\*\*:?\s*', '', section)
                            st.info(content)
                    
                    else:
                        # Other sections
                        if section.strip() and len(section.strip()) > 20:
                            with st.expander("📌 Additional Information", expanded=False):
                                st.markdown(section)

def render_custom_css():
    """Apply beautiful custom CSS styles"""
    load_custom_css()

def render_legal_footer():
    """Render beautiful legal disclaimer and footer"""
    st.divider()
    
    with st.expander("📜 Legal & Privacy Information"):
        st.markdown("""
        ### Legal Disclaimer
        This application provides plant information for educational purposes only. 
        Always consult professionals for plant care and safety advice.
        
        ### Privacy Policy
        - We only collect plant search queries
        - Data may be cached for performance
        - No personal information is stored
        - OpenAI processes plant analysis requests
        
        ### Copyright
        © 2024 Plant Facts Explorer by Maniwar
        Released under MIT License
        """)
    
    # Beautiful footer
    st.markdown("""
    <div class="footer-container">
        <h3>🌿 Plant Facts Explorer</h3>
        <p>Made with ❤️ by Maniwar • Version 2.3.0</p>
        <p style="opacity: 0.8; font-size: 0.9rem;">© 2024 • Powered by OpenAI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
