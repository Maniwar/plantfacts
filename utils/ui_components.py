"""
UI Components Module
Reusable UI components with better image handling and improved UX
Author: Maniwar
Version: 2.7.0 - Cards (no expanders), cleaned headers, robust images
"""

import re
import urllib.parse
from io import BytesIO
from typing import Dict

import streamlit as st
from gtts import gTTS


# =========================
# Global CSS / Theming
# =========================
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

        /* Analysis header bar */
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

        /* Cards (replace expanders) */
        .section-card {
            border: 2px solid var(--card-border, #e2e8f0);
            border-radius: 16px;
            padding: 0;
            margin-bottom: 1rem;
            overflow: hidden;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        }
        [data-theme="dark"] .section-card {
            --card-border: #475569;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        }
        .section-card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0.75rem 1rem;
            background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
            font-weight: 700;
        }
        .section-card-title {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'Space Grotesk', sans-serif;
        }
        .section-card-body {
            padding: 1rem 1.25rem;
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
            bottom: 0; left: 0; right: 0;
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
            .header-text h1 { font-size: 2rem; }
            .header-icon { font-size: 48px; }
            .header-container { padding: 2rem 1.5rem; }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    header_html = """
    <div class="header-container">
        <div class="header-content">
            <div class="header-icon">🌿</div>
            <div class="header-text">
                <h1>Plant Facts Explorer</h1>
                <p>Discover the amazing world of plants with AI-powered insights</p>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# =========================
# Media helpers
# =========================
def get_plant_image_url(plant_name: str) -> str:
    """
    Return a robust image URL; prefer Picsum (always-on), then known-good photos.
    """
    clean_name = urllib.parse.quote(plant_name.lower())
    # 1) Always-on placeholder with a stable seed
    picsum = f"https://picsum.photos/seed/{clean_name}/800/600"

    # 2) Known-good curated images (used only for common plants)
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
        "bamboo": "https://images.pexels.com/photos/279321/pexels-photo-279321.jpeg?auto=compress&cs=tinysrgb&w=800",
    }

    for key, url in common_plants.items():
        if key in plant_name.lower():
            # If a curated match found, still prefer Picsum if remote host blocks hotlinking
            return picsum

    return picsum  # default reliable source


# =========================
# Content helpers
# =========================
def extract_quick_facts(analysis: str) -> Dict[str, str]:
    """
    Extract quick facts from plant analysis
    """
    facts: Dict[str, str] = {}
    analysis_lower = analysis.lower()

    # Toxicity
    if "toxic" in analysis_lower:
        if ("not toxic" in analysis_lower) or ("non-toxic" in analysis_lower) or ("non toxic" in analysis_lower):
            facts["Safety"] = "Pet Safe ✅"
        else:
            facts["Safety"] = "Toxic ⚠️"

    # Light
    for pattern, display in {
        "full sun": "☀️ Full Sun",
        "partial shade": "⛅ Partial",
        "full shade": "🌙 Shade",
        "bright indirect": "💡 Bright",
        "low light": "🔅 Low Light",
    }.items():
        if pattern in analysis_lower:
            facts["Light"] = display
            break

    # Water
    for pattern, display in {
        "daily": "💧 Daily",
        "weekly": "💦 Weekly",
        "moderate": "💧 Moderate",
        "drought": "🌵 Minimal",
    }.items():
        if pattern in analysis_lower:
            facts["Water"] = display
            break

    # Origin
    origin_match = re.search(r"native to ([^,\.]+)", analysis_lower)
    if origin_match:
        origin = origin_match.group(1).title()
        facts["Origin"] = f"🌍 {origin}"

    return facts


def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech conversion
    """
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\#\#(.*?)\n", r"\1. ", text)
    text = re.sub(r"\#(.*?)\n", r"\1. ", text)
    text = re.sub(r"\* (.*?)\n", r"\1. ", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = text.replace("|", ", ").replace("-", " ").replace("`", "")
    return text


def _normalize_subheaders(md: str) -> str:
    """
    Normalize noisy '###' / '####' headings inside LLM content.
    - Convert lines starting with '##'+' to bold labels (e.g., '### Common Name:' -> '**Common Name:**')
    - Keep lists/paragraphs intact.
    """
    def repl(m: re.Match) -> str:
        title = m.group(1).strip()
        # Ensure trailing colon for a neat label
        if not title.endswith(":"):
            title += ":"
        return f"**{title}**"

    # Convert H2-H6 single-line headings to bold labels
    md = re.sub(r"^\s*#{2,6}\s+([^\n#].*?)\s*$", repl, md, flags=re.MULTILINE)
    return md


# =========================
# Section parsing (titles + icons)
# =========================
def _parse_section_meta(section: str):
    """
    Return (icon, title, content, style) for a section.
    style ∈ {"markdown","info","warning","success"} to control rendering.
    """
    raw = section.strip()
    lower = raw.lower()

    heading_patterns = [
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(general information)\s*:?\s*\*\*\s*', "📝", "markdown"),
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(care instructions)\s*:?\s*\*\*\s*', "🌱", "markdown"),
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(toxicity)\s*:?\s*\*\*\s*', "⚠️", "warning"),
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(propagation)\s*:?\s*\*\*\s*', "🌿", "markdown"),
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(common issues|problems)\s*:?\s*\*\*\s*', "🐛", "markdown"),
        (r'^\s*\*\*\s*(?:\d+\.\s*)?(interesting facts)\s*:?\s*\*\*\s*', "💡", "info"),
    ]

    for pat, icon, style in heading_patterns:
        m = re.search(pat, raw, flags=re.IGNORECASE)
        if m:
            title = m.group(1).title()
            content = raw[m.end():].strip()
            if "toxicity" in title.lower() and (("not toxic" in lower) or ("non-toxic" in lower) or ("non toxic" in lower)):
                style = "success"
            return icon, title, content, style

    # Keyword fallback
    for key, icon, style in [
        ("general information", "📝", "markdown"),
        ("care instructions", "🌱", "markdown"),
        ("toxicity", "⚠️", "warning"),
        ("propagation", "🌿", "markdown"),
        ("common issues", "🐛", "markdown"),
        ("problems", "🐛", "markdown"),
        ("interesting facts", "💡", "info"),
    ]:
        if key in lower:
            title = key.title()
            if "toxicity" in key and (("not toxic" in lower) or ("non-toxic" in lower) or ("non toxic" in lower)):
                style = "success"
            return icon, title, raw, style

    # Fallback: first line
    first_line = raw.splitlines()[0] if raw else "Details"
    title = first_line.split(":")[0].strip()
    if len(title) > 60:
        title = " ".join(title.split()[:8])
    return "📌", (title or "Details"), raw, "markdown"


def _render_section_card(icon: str, title: str, content: str, style: str = "markdown"):
    """
    Render a section as a styled card (no expanders).
    """
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-card-header">
                <span class="section-card-title">{icon} {title}</span>
            </div>
            <div class="section-card-body">
        """,
        unsafe_allow_html=True,
    )

    content = _normalize_subheaders(content)

    # Body content
    if style == "warning":
        st.warning(content)
    elif style == "success":
        st.success(content)
    elif style == "info":
        st.info(content)
    else:
        st.markdown(content)

    st.markdown("</div></div>", unsafe_allow_html=True)


# =========================
# Main renderer
# =========================
def render_plant_analysis_display(plant_name: str, analysis: str, mute_audio: bool = True):
    """
    Render beautiful plant analysis display with cards (no expanders)
    """
    with st.container():
        # Header bar
        st.markdown(
            f"""
            <div class="analysis-header">
                <span>🌱</span>
                <span>Analysis: {plant_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Two columns
        col1, col2 = st.columns([2, 3], gap="large")

        with col1:
            # Robust image (prefer always-on source)
            image_url = get_plant_image_url(plant_name)
            st.image(image_url, caption=f"🌿 {plant_name}", use_container_width=True)

            # Quick Facts
            st.markdown("### ⭐ Quick Facts")
            facts = extract_quick_facts(analysis)
            if facts:
                fact_cols = st.columns(2)
                for i, (label, value) in enumerate(facts.items()):
                    with fact_cols[i % 2]:
                        st.metric(label=label, value=value)

            # Audio (optional)
            if not mute_audio:
                st.markdown("### 🔊 Audio Guide")
                with st.spinner("Generating audio..."):
                    try:
                        clean_analysis = clean_text_for_tts(analysis)
                        audio_stream = BytesIO()
                        gTTS(text=clean_analysis, lang="en").write_to_fp(audio_stream)
                        st.audio(audio_stream, format="audio/mpeg")
                    except Exception as e:
                        st.warning(f"Audio unavailable: {str(e)}")

        with col2:
            # Detailed Information
            st.markdown("### 📋 Detailed Information")

            # Split on 2+ newlines to keep paragraphs/lists together
            sections = re.split(r"\n{2,}", analysis.strip())

            # If the first chunk is an overall title/intro, render as a top card
            if sections and len(sections[0].strip()) > 0:
                intro = sections[0]
                # If it's obviously a title (starts with '#', or contains 'Report on' etc.)
                if intro.lstrip().startswith("#") or "report on" in intro.lower():
                    _render_section_card("📌", "Overview", intro, "markdown")
                    sections = sections[1:]  # consume it

            # Render remaining sections as cards
            for section in sections:
                if not section.strip():
                    continue
                icon, title, content, style = _parse_section_meta(section)
                _render_section_card(icon, title, content, style)


# =========================
# Public helpers
# =========================
def render_custom_css():
    """Apply beautiful custom CSS styles with dark theme support"""
    load_custom_css()


def render_legal_footer():
    """Render beautiful legal disclaimer and footer"""
    st.divider()

    with st.expander("📜 Legal & Privacy Information"):
        st.markdown(
            """
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
            """
        )

    st.markdown(
        """
        <div class="footer-container">
            <h3>🌿 Plant Facts Explorer</h3>
            <p>Made with ❤️ by Maniwar • Version 2.7.0</p>
            <p style="opacity: 0.8; font-size: 0.9rem;">© 2024 • Powered by OpenAI & Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backwards compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)
