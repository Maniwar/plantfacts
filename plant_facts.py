"""
UI Components Module
Reusable UI components with better image handling and improved UX
Author: Maniwar
Version: 2.5.0 - Better images and expanded sections for better UX
"""

import streamlit as st
import re
from gtts import gTTS
from io import BytesIO
from typing import Dict, Optional
import urllib.parse

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
        
        /* Beautiful Header - works in both themes */
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
        
        /* Analysis Container */
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
        
        /* Metrics */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid #e2e8f0;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Dark theme metric adjustment */
        [data-theme="dark"] [data-testid="metric-container"] {
            background: rgba(30, 41, 59, 0.9);
            border-color: #475569;
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
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Buttons */
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
        
        /* Success/Info/Warning */
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
        
        /* Expander headers */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        /* Images */
        .stImage {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        
        /* Plant image container */
        .plant-image-container {
            position: relative;
            width: 100%;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        }
        
        .plant-image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .plant-image-caption {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
            padding: 1rem;
            color: white;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        /* Divider */
        hr {
            margin: 3rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
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

def get_plant_image_url(plant_name: str) -> str:
    """
    Get a reliable plant image URL using multiple fallback sources
    """
    # Clean the plant name for URL
    clean_name = urllib.parse.quote(plant_name.lower())
    
    # List of image sources to try (in order of preference)
    image_sources = [
        # 1. Pexels (reliable, high quality)
        f"https://images.pexels.com/photos/1407305/pexels-photo-1407305.jpeg?auto=compress&cs=tinysrgb&w=800",  # Generic beautiful plant
        
        # 2. Picsum (Lorem Picsum - always works)
        f"https://picsum.photos/seed/{clean_name}/800/600",
        
        # 3. Unsplash with specific collection
        f"https://source.unsplash.com/800x600/?{clean_name},plant,flower,botanical",
        
        # 4. Generic plant image from Pexels
        "https://images.pexels.com/photos/1072179/pexels-photo-1072179.jpeg?auto=compress&cs=tinysrgb&w=800"
    ]
    
    # For common plants, use specific known good images
    common_plants = {
        "rose": "https://images.pexels.com/photos/56866/garden-rose-red-pink-56866.jpeg?auto=compress&cs=tinysrgb&w=800",
        "cactus": "https://images.pexels.com/photos/1903965/pexels-photo-1903965.jpeg?auto=compress&cs=tinysrgb&w=800",
        "monstera": "https://images.pexels.com/photos/3644742/pexels-photo-3644742.jpeg?auto=compress&cs=tinysrgb&w=800",
        "succulent": "https://images.pexels.com/photos/1011302/pexels-photo-1011302.jpeg?auto=compress&cs=tinysrgb&w=800",
        "orchid": "https://images.pexels.com/photos/16868886/pexels-photo-16868886.jpeg?auto=compress&cs=tinysrgb&w=800",
        "fern": "https://images.pexels.com/photos/1470171/pexels-photo-1470171.jpeg?auto=compress&cs=tinysrgb&w=800",
        "tulip": "https://images.pexels.com/photos/54332/tulip-flower-blossom-bloom-54332.jpeg?auto=compress&cs=tinysrgb&w=800",
        "sunflower": "https://images.pexels.com/photos/46216/sunflower-flowers-bright-yellow-46216.jpeg?auto=compress&cs=tinysrgb&w=800",
        "lavender": "https://images.pexels.com/photos/207518/pexels-photo-207518.jpeg?auto=compress&cs=tinysrgb&w=800",
        "bamboo": "https://images.pexels.com/photos/279321/pexels-photo-279321.jpeg?auto=compress&cs=tinysrgb&w=800"
    }
    
    # Check if we have a specific image for this plant
    for key, url in common_plants.items():
        if key in plant_name.lower():
            return url
    
    # Use Picsum as reliable fallback with seed based on plant name
    return f"https://picsum.photos/seed/{clean_name}/800/600"

def extract_quick_facts(analysis: str) -> Dict[str, str]:
    """
    Extract quick facts from plant analysis
    """
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
    Render beautiful plant analysis display with better UX (expanded sections)
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
            # Plant image with reliable source
            image_url = get_plant_image_url(plant_name)
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
            # Detailed analysis - EXPANDED BY DEFAULT for better UX
            st.markdown("### 📋 Detailed Information")
            
            # Parse and display sections properly
            sections = analysis.split('\n\n')
            
            # Track which sections we've already displayed
            displayed_sections = set()
            
            for section in sections:
                if section.strip() and len(section.strip()) > 20:
                    section_lower = section.lower()
                    
                    # Check for General Information
                    if any(x in section_lower for x in ["general information", "**1."]) and "general" not in displayed_sections:
                        displayed_sections.add("general")
                        # Just show the content without the redundant header
                        with st.expander("📝 General Information", expanded=True):
                            # Remove ALL headers and numbers from content
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:General Information:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*General Information\s*', '', content, flags=re.MULTILINE)
                            st.markdown(content.strip())
                    
                    # Check for Care Instructions
                    elif any(x in section_lower for x in ["care instructions", "**2."]) and "care" not in displayed_sections:
                        displayed_sections.add("care")
                        with st.expander("🌱 Care Instructions", expanded=True):
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:Care Instructions:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*Care Instructions\s*', '', content, flags=re.MULTILINE)
                            st.markdown(content.strip())
                    
                    # Check for Toxicity/Safety
                    elif any(x in section_lower for x in ["toxicity", "**3."]) and "toxicity" not in displayed_sections:
                        displayed_sections.add("toxicity")
                        is_toxic = "toxic" in section_lower and "not toxic" not in section_lower
                        with st.expander("⚠️ Safety Information", expanded=True):
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:Toxicity:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*Toxicity\s*', '', content, flags=re.MULTILINE)
                            if is_toxic:
                                st.warning(content.strip())
                            else:
                                st.success(content.strip())
                    
                    # Check for Propagation
                    elif any(x in section_lower for x in ["propagation", "**4."]) and "propagation" not in displayed_sections:
                        displayed_sections.add("propagation")
                        with st.expander("🌿 Propagation Methods", expanded=True):
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:Propagation:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*Propagation\s*', '', content, flags=re.MULTILINE)
                            st.markdown(content.strip())
                    
                    # Check for Common Issues
                    elif any(x in section_lower for x in ["common issues", "problems", "**5."]) and "issues" not in displayed_sections:
                        displayed_sections.add("issues")
                        with st.expander("🐛 Common Issues & Solutions", expanded=False):
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:Common Issues:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*Common Issues\s*', '', content, flags=re.MULTILINE)
                            st.markdown(content.strip())
                    
                    # Check for Interesting Facts
                    elif any(x in section_lower for x in ["interesting facts", "**6."]) and "facts" not in displayed_sections:
                        displayed_sections.add("facts")
                        with st.expander("💡 Interesting Facts", expanded=True):
                            content = re.sub(r'\*\*(?:\d+\.?\s*)?(?:Interesting Facts:?)\*\*:?\s*', '', section)
                            content = re.sub(r'^#+\s*Interesting Facts\s*', '', content, flags=re.MULTILINE)
                            st.info(content.strip())
                    
                    # For subsections within main sections, extract headers and create appropriate expanders
                    else:
                        # Try to extract a meaningful header from the section
                        header_match = re.match(r'^(?:\*\*)?([A-Z][^:*\n]+)(?:\*\*)?[:.]?\s*', section)
                        if header_match:
                            header = header_match.group(1).strip()
                            content = section[header_match.end():].strip()
                            
                            # Choose appropriate icon based on content
                            icon = "📌"
                            if any(word in header.lower() for word in ["origin", "habitat", "native"]):
                                icon = "🌍"
                            elif any(word in header.lower() for word in ["description", "appearance", "physical"]):
                                icon = "👁️"
                            elif any(word in header.lower() for word in ["scientific", "name", "species"]):
                                icon = "🔬"
                            elif any(word in header.lower() for word in ["common name"]):
                                icon = "📛"
                            
                            # Only create expander if we have substantial content
                            if content and len(content) > 20:
                                with st.expander(f"{icon} {header}", expanded=True):
                                    st.markdown(content)

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
        <p>Made with ❤️ by Maniwar • Version 2.5.1</p>
        <p style="opacity: 0.8; font-size: 0.9rem;">© 2024 • Powered by OpenAI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# For backward compatibility
def get_plant_image(plant_name: str) -> str:
    """Legacy function - redirects to new image function"""
    return get_plant_image_url(plant_name)
