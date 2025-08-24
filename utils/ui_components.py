"""
UI Components Module
Reusable UI components with dark theme support and image fallback
Author: Maniwar
Version: 2.4.0 - Dark theme support and image fallback
"""

import streamlit as st
import re
from gtts import gTTS
from io import BytesIO
from typing import Dict, Optional
import base64

def get_fallback_plant_svg():
    """
    Generate a beautiful fallback plant SVG when image fails to load
    """
    svg = """
    <svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="potGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#92400e;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#78350f;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Background circle -->
        <circle cx="200" cy="200" r="190" fill="#f0fdf4" opacity="0.3"/>
        
        <!-- Pot -->
        <path d="M 150 250 L 170 350 L 230 350 L 250 250 Z" fill="url(#potGradient)"/>
        <rect x="140" y="240" width="120" height="20" rx="5" fill="#92400e"/>
        
        <!-- Stem -->
        <rect x="195" y="180" width="10" height="80" fill="#059669"/>
        
        <!-- Leaves -->
        <ellipse cx="180" cy="180" rx="30" ry="50" fill="url(#leafGradient)" transform="rotate(-20 180 180)"/>
        <ellipse cx="220" cy="180" rx="30" ry="50" fill="url(#leafGradient)" transform="rotate(20 220 180)"/>
        <ellipse cx="200" cy="150" rx="25" ry="45" fill="url(#leafGradient)"/>
        
        <!-- Decorative dots -->
        <circle cx="150" cy="150" r="3" fill="#10b981" opacity="0.5"/>
        <circle cx="250" cy="160" r="3" fill="#10b981" opacity="0.5"/>
        <circle cx="160" cy="220" r="3" fill="#10b981" opacity="0.5"/>
        <circle cx="240" cy="210" r="3" fill="#10b981" opacity="0.5"/>
    </svg>
    """
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"

def load_custom_css():
    """
    Load custom CSS with dark theme support
    """
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');
        
        /* Hide weird 0 and empty elements */
        .stMarkdown p:empty,
        span:empty,
        div[data-testid="stMarkdownContainer"] > p:empty {
            display: none !important;
        }
        
        /* Global App Styling with dark theme support */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Light theme */
        [data-theme="light"] {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-color: rgba(0,0,0,0.1);
        }
        
        /* Dark theme */
        [data-theme="dark"], 
        .stApp[data-testid="stApp"][data-theme="dark"],
        [data-testid="stAppViewContainer"][data-theme="dark"] {
            --bg-primary: #1e293b;
            --bg-secondary: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --border-color: #475569;
            --shadow-color: rgba(0,0,0,0.3);
        }
        
        /* Beautiful Header - works in both themes */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px var(--shadow-color);
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
        
        /* Analysis Container - dark theme compatible */
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
        
        /* Metrics - dark theme aware */
        [data-testid="metric-container"] {
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px var(--shadow-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
            border-color: #667eea;
        }
        
        [data-testid="metric-container"] label {
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Buttons - always gradient */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
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
        
        /* Container with border - dark theme compatible */
        .stContainer > div {
            background: var(--bg-primary);
            color: var(--text-primary);
        }
        
        /* Success/Info/Warning - vibrant in both themes */
        .stSuccess {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: none;
            font-weight: 500;
        }
        
        .stInfo {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: none;
            font-weight: 500;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: none;
            font-weight: 500;
        }
        
        /* Radio buttons - dark theme compatible */
        .stRadio > div[role="radiogroup"] {
            background: var(--bg-secondary);
            padding: 0.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px var(--shadow-color);
        }
        
        /* Expander - dark theme compatible */
        .streamlit-expanderHeader {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 12px;
            font-weight: 600;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: var(--bg-primary);
        }
        
        /* Images */
        .stImage {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px var(--shadow-color);
        }
        
        /* Plant fallback image container */
        .plant-fallback {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-radius: 16px;
            padding: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 300px;
        }
        
        /* Dark mode plant fallback */
        [data-theme="dark"] .plant-fallback {
            background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        }
        
        /* Divider */
        hr {
            margin: 3rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        }
        
        /* Footer - works in both themes */
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

def render_plant_image_with_fallback(plant_name: str):
    """
    Render plant image with fallback to beautiful SVG if image fails
    """
    from utils.config import AppConfig
    config = AppConfig()
    
    # Try Unsplash image
    image_url = f"https://source.unsplash.com/{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}/?{plant_name.replace(' ', ',')},plant,botanical,nature"
    
    # Create HTML with fallback
    image_html = f"""
    <div style="position: relative; width: 100%; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
        <img src="{image_url}" 
             alt="{plant_name}" 
             style="width: 100%; height: auto; display: block; border-radius: 16px;"
             onerror="this.onerror=null; this.src='{get_fallback_plant_svg()}';">
        <div style="position: absolute; bottom: 0; left: 0; right: 0; 
                    background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
                    padding: 1rem; border-radius: 0 0 16px 16px;">
            <p style="color: white; margin: 0; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                🌿 {plant_name}
            </p>
        </div>
    </div>
    """
    
    st.markdown(image_html, unsafe_allow_html=True)

def get_plant_image(plant_name: str) -> str:
    """
    Get a plant image URL from Unsplash (keeping for backward compatibility)
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
    Render beautiful plant analysis display with dark theme support
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
            # Plant image with fallback
            render_plant_image_with_fallback(plant_name)
            
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
    """Apply beautiful custom CSS styles with dark theme support"""
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
        <p>Made with ❤️ by Maniwar • Version 2.4.0</p>
        <p style="opacity: 0.8; font-size: 0.9rem;">© 2024 • Powered by OpenAI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
