"""
UI Components Module - Simplified Version
Clean, minimal UI components without animations and visual clutter
Author: Maniwar (Simplified)
Version: 2.0.0
"""

import streamlit as st
import requests
import hashlib
from typing import Dict, Optional
from urllib.parse import quote
import html as _html

def apply_clean_theme():
    """Apply a clean, minimal theme to the app"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Base styling */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #ffffff;
        }
        
        /* Hide Streamlit defaults */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Clean containers */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Card components */
        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f3f4f6;
        }
        
        /* Status indicators */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-warning {
            background: #fed7aa;
            color: #92400e;
        }
        
        .status-info {
            background: #dbeafe;
            color: #1e40af;
        }
        
        /* Buttons */
        .stButton > button {
            background: #059669;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 6px;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .stButton > button:hover {
            background: #047857;
        }
        
        /* Info sections */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .info-item {
            padding: 1rem;
            background: #f9fafb;
            border-radius: 6px;
        }
        
        .info-label {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            font-size: 1.125rem;
            font-weight: 600;
            color: #111827;
        }
        
        /* Reduce spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 900px;
        }
        
        /* Clean headers */
        h1 {
            color: #111827;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #059669;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        h3 {
            color: #374151;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Text content */
        p {
            line-height: 1.6;
            color: #4b5563;
        }
        
        /* Lists */
        ul, ol {
            line-height: 1.8;
            color: #4b5563;
        }
        
        /* Code blocks */
        code {
            background: #f3f4f6;
            padding: 0.125rem 0.25rem;
            border-radius: 3px;
            font-size: 0.875rem;
        }
        
        /* Streamlit specific overrides */
        .stSelectbox > div > div {
            background: white;
            border: 1px solid #e5e7eb;
        }
        
        .stTextInput > div > div {
            background: white;
            border: 1px solid #e5e7eb;
        }
        
        /* Success/Error messages */
        .stAlert {
            border-radius: 6px;
        }
        
        /* Metrics */
        [data-testid="metric-container"] {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            padding: 1rem;
            border-radius: 6px;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #059669;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)


def render_simple_header(title: str = "Plant Facts Explorer", 
                        subtitle: str = "AI-powered plant identification and care guide"):
    """Render a simple, clean header without animations"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌿 {_html.escape(title)}</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">{_html.escape(subtitle)}</p>
    </div>
    """, unsafe_allow_html=True)


def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """Render a clean information card"""
    st.markdown(f"""
    <div class="card">
        <div class="card-header">{icon} {_html.escape(title)}</div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(text: str, status: str = "info"):
    """Render a status badge
    
    Args:
        text: Badge text
        status: One of 'success', 'warning', 'info'
    """
    status_class = f"status-{status}"
    st.markdown(f"""
    <span class="status-badge {status_class}">{_html.escape(text)}</span>
    """, unsafe_allow_html=True)


def render_quick_facts(facts: Dict[str, str]):
    """Render quick facts in a clean grid"""
    if not facts:
        return
    
    cols = st.columns(min(len(facts), 3))
    for i, (label, value) in enumerate(facts.items()):
        with cols[i % len(cols)]:
            st.metric(label=label, value=value)


def display_plant_card(plant_name: str, 
                       image_url: str, 
                       quick_facts: Dict[str, str],
                       description: str = None):
    """Display a clean plant information card"""
    
    st.markdown(f"""
    <div class="card">
        <h2 style="color: #059669; margin-top: 0;">🌱 {_html.escape(plant_name)}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image_url, caption=plant_name, use_container_width=True)
    
    with col2:
        st.markdown("### Quick Facts")
        if quick_facts:
            for label, value in quick_facts.items():
                st.markdown(f"""
                <div class="info-item">
                    <div class="info-label">{_html.escape(label)}</div>
                    <div class="info-value">{_html.escape(value)}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No quick facts available")
    
    if description:
        st.markdown("### Description")
        st.markdown(description)


def render_search_suggestions(suggestions: list, max_display: int = 5):
    """Render search suggestions as clickable chips"""
    if not suggestions:
        return None
    
    suggestions = suggestions[:max_display]
    
    st.markdown("**Suggestions:**")
    cols = st.columns(len(suggestions))
    
    selected = None
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                selected = suggestion
    
    return selected


def create_loading_placeholder(message: str = "Loading..."):
    """Create a clean loading placeholder"""
    return st.empty().info(f"⏳ {message}")


def render_error_message(message: str):
    """Render a clean error message"""
    st.error(f"❌ {message}")


def render_success_message(message: str):
    """Render a clean success message"""
    st.success(f"✅ {message}")


def render_info_message(message: str):
    """Render a clean info message"""
    st.info(f"ℹ️ {message}")


# Simplified image fetching (keep existing logic but simplify)
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_simple(plant_name: str) -> str:
    """Get a plant image URL with fallback to placeholder"""
    
    # Try Wikipedia first (fastest and most reliable)
    try:
        search_name = plant_name.replace(" ", "_")
        response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(search_name)}",
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            if "thumbnail" in data:
                return data["thumbnail"]["source"]
    except:
        pass
    
    # Fallback to Unsplash
    search_terms = quote(f"{plant_name},plant,botanical")
    return f"https://source.unsplash.com/800x600/?{search_terms}"


def extract_quick_facts_simple(analysis: str) -> Dict[str, str]:
    """Extract key facts from analysis text (simplified)"""
    facts = {}
    lower_text = analysis.lower()
    
    # Safety check
    if "toxic" in lower_text:
        if any(word in lower_text for word in ["non-toxic", "not toxic", "safe"]):
            facts["Safety"] = "Pet Safe ✅"
        else:
            facts["Toxicity"] = "Toxic ⚠️"
    
    # Light requirements
    light_conditions = {
        "full sun": "Full Sun ☀️",
        "partial shade": "Partial Shade ⛅",
        "bright indirect": "Bright Indirect 💡",
        "low light": "Low Light 🔅"
    }
    
    for key, value in light_conditions.items():
        if key in lower_text:
            facts["Light"] = value
            break
    
    # Watering
    if "daily" in lower_text or "every day" in lower_text:
        facts["Water"] = "Daily 💧"
    elif "weekly" in lower_text or "once a week" in lower_text:
        facts["Water"] = "Weekly 💦"
    elif "moderate" in lower_text:
        facts["Water"] = "Moderate 💧"
    elif "drought" in lower_text or "minimal" in lower_text:
        facts["Water"] = "Minimal 🌵"
    
    return facts


def render_minimal_footer():
    """Render a minimal footer"""
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding-top: 2rem; 
                border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.875rem;">
        Plant Facts Explorer • AI-Powered Plant Guide<br>
        <small>For informational purposes only</small>
    </div>
    """, unsafe_allow_html=True)