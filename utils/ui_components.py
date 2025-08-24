"""
UI Components Module
Reusable UI components for the Plant Facts Explorer
"""

import streamlit as st
import re
from gtts import gTTS
from io import BytesIO
from typing import Dict, Optional
from utils.config import AppConfig

config = AppConfig()

def render_custom_css():
    """Render custom CSS styles for the application"""
    st.markdown("""
    <style>
        /* Import fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        /* Global styles */
        .stApp {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Header styling */
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
        }
        
        .header-text p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.95;
        }
        
        /* Card styles */
        .info-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* Plant image styling */
        .plant-image-container {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            margin-bottom: 2rem;
        }
        
        .plant-image-container img {
            width: 100%;
            height: auto;
        }
        
        /* Quick facts grid */
        .facts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .fact-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .fact-card:hover {
            transform: scale(1.05);
        }
        
        .fact-label {
            font-size: 0.85rem;
            opacity: 0.9;
            margin-bottom: 0.3rem;
        }
        
        .fact-value {
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        /* Input selector */
        .input-selector {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
        
        /* Success animation */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-in {
            animation: slideIn 0.5s ease-out;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .header-text h1 {
                font-size: 1.8rem;
            }
            .header-icon {
                font-size: 40px;
            }
            .facts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

def render_header():
    """Render the application header"""
    st.markdown("""
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
    """, unsafe_allow_html=True)

def get_plant_image(plant_name: str) -> str:
    """
    Get a plant image URL from Unsplash
    
    Args:
        plant_name: Name of the plant
        
    Returns:
        Image URL
    """
    # Using Unsplash Source API (no key required)
    return f"https://source.unsplash.com/{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}/?{plant_name.replace(' ', ',')},plant,nature"

def extract_quick_facts(analysis: str) -> Dict[str, str]:
    """
    Extract quick facts from plant analysis
    
    Args:
        analysis: Full plant analysis text
        
    Returns:
        Dictionary of quick facts
    """
    facts = {}
    
    # Toxicity check
    if "toxic" in analysis.lower():
        if "not toxic" in analysis.lower() or "non-toxic" in analysis.lower():
            facts["Toxicity"] = "Safe ✅"
        else:
            facts["Toxicity"] = "Toxic ⚠️"
    
    # Light requirements
    for pattern in config.LIGHT_PATTERNS:
        if pattern in analysis.lower():
            facts["Light"] = pattern.title()
            break
    
    # Watering needs
    for pattern, value in config.WATER_PATTERNS.items():
        if pattern in analysis.lower():
            facts["Water"] = value
            break
    
    # Origin
    origin_match = re.search(r'native to ([^,\.]+)', analysis.lower())
    if origin_match:
        facts["Origin"] = origin_match.group(1).title()
    
    return facts

def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech conversion
    
    Args:
        text: Raw text with markdown formatting
        
    Returns:
        Cleaned text suitable for TTS
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
    Render the plant analysis display with image and facts
    
    Args:
        plant_name: Name of the plant
        analysis: Plant analysis text
        mute_audio: Whether to mute audio generation
    """
    # Create two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        
        # Display plant image
        image_url = get_plant_image(plant_name)
        st.markdown(f'''
        <div class="plant-image-container">
            <img src="{image_url}" alt="{plant_name}">
        </div>
        ''', unsafe_allow_html=True)
        
        # Quick Facts Cards
        facts = extract_quick_facts(analysis)
        if facts:
            st.markdown("### 🌟 Quick Facts")
            st.markdown('<div class="facts-grid">', unsafe_allow_html=True)
            for label, value in facts.items():
                st.markdown(f'''
                <div class="fact-card">
                    <div class="fact-label">{label}</div>
                    <div class="fact-value">{value}</div>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Audio player
        if not mute_audio:
            with st.spinner("Generating audio..."):
                clean_analysis = clean_text_for_tts(analysis)
                audio_stream = BytesIO()
                tts = gTTS(text=clean_analysis, lang='en')
                tts.write_to_fp(audio_stream)
                st.audio(audio_stream, format="audio/mpeg", start_time=0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<h2 style="color: #667eea; margin-bottom: 1rem;">📋 Detailed Analysis: {plant_name}</h2>', 
                    unsafe_allow_html=True)
        
        # Parse and display analysis in cards
        sections = analysis.split('\n\n')
        for section in sections:
            if section.strip():
                # Determine icon based on section content
                icon = "📍"
                if "care" in section.lower():
                    icon = "🌱"
                elif "toxic" in section.lower():
                    icon = "⚠️"
                elif "propagat" in section.lower():
                    icon = "🌿"
                elif "issue" in section.lower() or "problem" in section.lower():
                    icon = "🐛"
                elif "fact" in section.lower():
                    icon = "💡"
                
                st.markdown(f'''
                <div class="info-card animate-in">
                    <div class="card-content">
                        {section}
                    </div>
                </div>
                ''', unsafe_allow_html=True)

def render_legal_footer():
    """Render the legal disclaimer and footer"""
    st.divider()
    with st.expander("📜 Legal and Data Privacy Statement", expanded=False):
        st.markdown("""
        <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <h4>Legal Statement</h4>
            <p style="font-size:14px;">
            This application ("App") is provided "as is" without any warranties, express or implied. 
            The information provided by the App is intended for informational purposes only and not as 
            a substitute for professional advice. Always seek qualified professional advice regarding plants.
            </p>
            
            <h4>Data Privacy Statement</h4>
            <p style="font-size:14px;">
            <b>Information Collection:</b> The App only collects plant name queries for service provision.
            <br><b>Information Usage:</b> Queries are used solely to provide plant analysis and are cached for performance.
            <br><b>Information Sharing:</b> We do not share your data with third parties except as necessary for the service.
            <br><b>Security:</b> We implement security measures but cannot guarantee complete security.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white;">
        <p style="margin: 0;">Made with ❤️ for Plant Enthusiasts</p>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">© 2025-  Maniwar</p>
    </div>
    """, unsafe_allow_html=True)
