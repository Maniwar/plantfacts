"""
UI Components Module
Verbatim LLM rendering + animations (leaf, sheen, typewriter), reliable images
Author: Maniwar
Version: 8.1.0 - Enhanced search support
"""

from __future__ import annotations

import html as _html
import re
from io import BytesIO
from typing import Dict, Optional
from urllib.parse import quote
import hashlib

import requests
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS


# =========================================================
# Global CSS with mobile optimization
# =========================================================
def load_custom_css() -> None:
    st.html(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

          :root {
            --grad-1:#667eea; --grad-2:#764ba2;
            --panel-radius:20px;
          }

          .stApp { font-family:'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

          /* Header - Mobile Optimized */
          .header {
            position:relative; overflow:hidden;
            background:linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 100%);
            padding: 1.2rem 1rem; 
            border-radius: var(--panel-radius);
            color:#fff; 
            box-shadow:0 16px 36px rgba(0,0,0,.15); 
            margin-bottom: 1rem;
            min-height: auto;
          }
          
          @media (min-width: 769px) {
            .header {
              padding: 2rem 1.5rem;
            }
          }
          
          .sheen { 
            position:absolute; top:-50%; right:-10%; width:60%; height:200%;
            background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
            animation: shimmer 3.5s ease-in-out infinite; 
            pointer-events:none; 
          }
          
          .title-row { 
            display:flex; 
            align-items:center; 
            gap:.5rem; 
            flex-wrap: nowrap;
          }
          
          .leaf { 
            font-size:1.8rem; 
            filter: drop-shadow(0 8px 16px rgba(0,0,0,.25));
            animation: float 4.5s ease-in-out infinite; 
            flex-shrink: 0;
          }
          
          .headline { 
            font-family:'Space Grotesk', sans-serif; 
            font-size: clamp(1.3rem, 5vw, 2rem); 
            font-weight:700; 
            line-height:1.1; 
            margin:0;
            word-break: break-word;
          }

          /* Subtitle - Responsive with different text */
          .subtitle-wrapper { 
            margin:.45rem 0 0 0; 
          }
          
          .subtitle-desktop, .subtitle-mobile {
            font-size: clamp(0.85rem, 3vw, 1rem);
            opacity: 0.95;
            line-height: 1.4;
            color: rgba(255, 255, 255, 0.95);
          }
          
          /* Show desktop subtitle with typewriter on larger screens */
          .subtitle-desktop {
            display: none;
          }
          
          @media (min-width: 769px) {
            .subtitle-desktop {
              display: inline-block;
              overflow: hidden;
              white-space: nowrap;
              border-right: .12em solid rgba(255,255,255,.85);
              animation: typing 3s steps(40,end), blink .85s step-end infinite;
              max-width: 100%;
            }
            .subtitle-mobile {
              display: none;
            }
          }
          
          /* Show mobile subtitle with wrapping on small screens */
          .subtitle-mobile {
            display: block;
            white-space: normal;
            animation: fadeIn 1s ease-out;
          }
          
          @media (min-width: 769px) {
            .subtitle-mobile {
              display: none;
            }
          }
          
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 0.95; transform: translateY(0); }
          }

          .bar-title {
            background:linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 100%);
            color:#fff; 
            font-weight:700; 
            padding:.8rem 1rem; 
            border-radius:12px;
            display:flex; 
            align-items:center; 
            gap:.6rem; 
            margin-top:.3rem;
            font-size: clamp(0.9rem, 3vw, 1.1rem);
          }

          .stImage { 
            border-radius:14px; 
            box-shadow:0 8px 24px rgba(0,0,0,.12); 
          }
          
          /* Streaming content animation */
          .streaming-content {
            animation: fadeInUp 0.3s ease-out;
          }
          
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          .typing-cursor {
            display: inline-block;
            width: 3px;
            height: 1.2em;
            background: var(--grad-2);
            animation: cursor-blink 1s infinite;
            margin-left: 2px;
            vertical-align: text-bottom;
          }
          
          @keyframes cursor-blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }

          /* Animations */
          @keyframes shimmer { 
            0%,100%{transform:translateX(0)} 
            50%{transform:translateX(18px)} 
          }
          
          @keyframes float { 
            0%,100%{transform:translateY(0) rotate(0deg)} 
            50%{transform:translateY(-10px) rotate(6deg)} 
          }
          
          @keyframes typing { 
            from{ width:0 } 
            to{ width:100% } 
          }
          
          @keyframes blink { 
            from, to { border-color: transparent } 
            50% { border-color: rgba(255,255,255,.85) } 
          }

          /* Mobile-specific adjustments */
          @media (max-width: 768px) {
            .header {
              padding: 1rem 0.8rem;
            }
            
            .title-row {
              gap: 0.3rem;
            }
            
            .leaf {
              font-size: 1.4rem;
            }
            
            .headline {
              font-size: 1.4rem !important;
            }
            
            .subtitle-wrapper {
              margin-top: 0.25rem;
            }
            
            .subtitle-mobile {
              font-size: 0.9rem !important;
            }
          }

          /* Respect reduced motion */
          @media (prefers-reduced-motion: reduce) {
            .sheen, .leaf, .typewriter, .streaming-content, .typing-cursor { 
              animation: none !important; 
            }
            .typewriter {
              border-right: none;
            }
          }

          /* Tidy default spacing from model text */
          .stMarkdown ul { margin:.3rem 0 .6rem 1rem; }
          .stMarkdown p:empty { display:none!important; }
        </style>
        """
    )


def render_header(
    subtitle: str = "Discover the amazing world of plants with AI-powered insights",
    subtitle_mobile: str = "AI-powered plant care guide",
    show_leaf: bool = True,
) -> None:
    """Render header with mobile-optimized layout"""
    leaf = '<span class="leaf">🌿</span>' if show_leaf else ""
    st.html(
        f"""
        <div class="header">
          <div class="sheen"></div>
          <div class="title-row">
            {leaf}
            <div class="headline">Plant Facts Explorer</div>
          </div>
          <div class="subtitle-wrapper">
            <div class="subtitle-desktop">{_html.escape(subtitle)}</div>
            <div class="subtitle-mobile">{_html.escape(subtitle_mobile)}</div>
          </div>
        </div>
        """
    )


# =========================================================
# Subtle, elegant particle effect
# =========================================================
def render_particles(
    enabled: bool = True,
    height: int = 100,
) -> None:
    """
    Subtle, elegant particle effect - just gentle floating dots
    Much more refined and less distracting
    """
    if not enabled:
        return

    from streamlit.components.v1 import html as _html_iframe
    
    # Very subtle, minimal particle effect
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                margin: 0; 
                padding: 0; 
                overflow: hidden; 
                background: transparent;
                height: 100vh;
                position: relative;
            }
            
            .particle-container {
                position: absolute;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            
            /* Subtle floating dots */
            .dot {
                position: absolute;
                width: 3px;
                height: 3px;
                background: rgba(102, 126, 234, 0.15);
                border-radius: 50%;
                animation: gentle-float 20s infinite ease-in-out;
            }
            
            .dot:nth-child(1) {
                left: 10%;
                animation-duration: 19s;
                animation-delay: 0s;
            }
            
            .dot:nth-child(2) {
                left: 20%;
                animation-duration: 21s;
                animation-delay: 3s;
            }
            
            .dot:nth-child(3) {
                left: 35%;
                animation-duration: 18s;
                animation-delay: 2s;
            }
            
            .dot:nth-child(4) {
                left: 50%;
                animation-duration: 22s;
                animation-delay: 5s;
            }
            
            .dot:nth-child(5) {
                left: 65%;
                animation-duration: 20s;
                animation-delay: 1s;
            }
            
            .dot:nth-child(6) {
                left: 80%;
                animation-duration: 23s;
                animation-delay: 4s;
            }
            
            .dot:nth-child(7) {
                left: 90%;
                animation-duration: 19s;
                animation-delay: 6s;
            }
            
            /* Very gentle floating animation */
            @keyframes gentle-float {
                0%, 100% {
                    transform: translateY(100vh) translateX(0);
                    opacity: 0;
                }
                10% {
                    opacity: 0.3;
                }
                90% {
                    opacity: 0.3;
                }
                100% {
                    transform: translateY(-20px) translateX(10px);
                    opacity: 0;
                }
            }
            
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .dot {
                    animation: none;
                    opacity: 0.1;
                }
            }
        </style>
    </head>
    <body>
        <div class="particle-container">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </body>
    </html>
    """
    
    _html_iframe(html_code, height=height, scrolling=False)


# =========================================================
# Streaming content with typewriter effect
# =========================================================
def render_streaming_content(content: str, container) -> None:
    """
    Render streaming content with typewriter-like animation
    """
    # Add a cursor at the end for typewriter effect
    html_content = f"""
    <div class="streaming-content">
        <div style="white-space: pre-wrap; font-family: inherit;">
            {_html.escape(content)}<span class="typing-cursor"></span>
        </div>
    </div>
    """
    container.markdown(html_content, unsafe_allow_html=True)


# =========================================================
# Improved Plant Image Service with multiple sources
# =========================================================
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_from_pexels(plant_name: str) -> Optional[Dict[str, str]]:
    """Try to get plant image from Pexels API (requires API key in secrets)"""
    try:
        if "PEXELS_API_KEY" in st.secrets:
            headers = {"Authorization": st.secrets["PEXELS_API_KEY"]}
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={quote(plant_name + ' plant')}&per_page=1",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    photo = data["photos"][0]
                    return {
                        "url": photo["src"]["large"],
                        "caption": f"Photo by {photo['photographer']} on Pexels",
                        "page_url": photo["url"]
                    }
    except:
        pass
    return None


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_from_gbif(plant_name: str) -> Optional[Dict[str, str]]:
    """Try to get plant image from GBIF (Global Biodiversity Information Facility)"""
    try:
        search_response = requests.get(
            f"https://api.gbif.org/v1/species/match?name={quote(plant_name)}",
            timeout=5
        )
        if search_response.status_code == 200:
            species_data = search_response.json()
            if species_data.get("usageKey"):
                media_response = requests.get(
                    f"https://api.gbif.org/v1/species/{species_data['usageKey']}/media",
                    timeout=5
                )
                if media_response.status_code == 200:
                    media_data = media_response.json()
                    results = media_data.get("results", [])
                    images = [r for r in results if r.get("type") == "StillImage" and r.get("identifier")]
                    if images:
                        img = images[0]
                        return {
                            "url": img["identifier"],
                            "caption": f"Source: GBIF - {species_data.get('scientificName', plant_name)}",
                            "page_url": f"https://www.gbif.org/species/{species_data['usageKey']}"
                        }
    except:
        pass
    return None


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_from_wikipedia(plant_name: str) -> Optional[Dict[str, str]]:
    """Enhanced Wikipedia image search"""
    try:
        title = _normalize_plant_title(plant_name)
        js = _wiki_summary(title)
        
        if not js:
            search_response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": f'{plant_name} (plant OR flower OR tree OR shrub)',
                    "utf8": 1,
                    "format": "json",
                    "srlimit": 10,
                },
                timeout=6,
            )
            if search_response.status_code == 200:
                hits = search_response.json().get("query", {}).get("search", [])
                for hit in hits:
                    js = _wiki_summary(hit["title"])
                    if js and (js.get("thumbnail") or js.get("originalimage")):
                        break

        if js:
            img = (js.get("thumbnail") or {}).get("source") or (js.get("originalimage") or {}).get("source")
            if img:
                page = (js.get("content_urls") or {}).get("desktop", {}).get("page")
                return {"url": img, "caption": f"Wikipedia: {js.get('title')}", "page_url": page}
    except:
        pass
    return None


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_from_unsplash(plant_name: str) -> Dict[str, str]:
    """Get a relevant plant image from Unsplash using their public CDN"""
    seed = hashlib.md5(plant_name.encode()).hexdigest()[:10]
    search_terms = quote(f"{plant_name},plant,botanical,nature")
    
    return {
        "url": f"https://source.unsplash.com/800x600/?{search_terms}",
        "caption": f"Plant image for {plant_name}",
        "page_url": None
    }


def _wiki_summary(title: str) -> Optional[dict]:
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}",
            timeout=6,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _normalize_plant_title(name: str) -> str:
    """Normalize common plant names to scientific names for better Wikipedia matches"""
    key = name.strip().lower()
    return {
        "tulip tree": "Liriodendron tulipifera",
        "yellow poplar": "Liriodendron tulipifera",
        "snake plant": "Dracaena trifasciata",
        "mother-in-law's tongue": "Dracaena trifasciata",
        "spider plant": "Chlorophytum comosum",
        "pothos": "Epipremnum aureum",
        "devil's ivy": "Epipremnum aureum",
        "money plant": "Epipremnum aureum",
        "peace lily": "Spathiphyllum",
        "rubber plant": "Ficus elastica",
        "rubber tree": "Ficus elastica",
        "zz plant": "Zamioculcas zamiifolia",
        "monstera": "Monstera deliciosa",
        "swiss cheese plant": "Monstera deliciosa",
        "fiddle leaf fig": "Ficus lyrata",
        "aloe": "Aloe vera",
        "jade plant": "Crassula ovata",
        "money tree": "Pachira aquatica",
        "bird of paradise": "Strelitzia",
        "boston fern": "Nephrolepis exaltata",
        "english ivy": "Hedera helix",
        "philodendron": "Philodendron hederaceum",
    }.get(key, name.strip())


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_info(plant_name: str) -> Dict[str, Optional[str]]:
    """Enhanced image fetching with multiple sources and better fallbacks"""
    # Try multiple sources in order
    result = get_plant_image_from_pexels(plant_name)
    if result and result.get("url"):
        return result
    
    result = get_plant_image_from_gbif(plant_name)
    if result and result.get("url"):
        return result
    
    result = get_plant_image_from_wikipedia(plant_name)
    if result and result.get("url"):
        return result
    
    return get_plant_image_from_unsplash(plant_name)


def get_plant_image_url(plant_name: str) -> str:
    """Backward compatibility helper"""
    return get_plant_image_info(plant_name)["url"]


# =========================================================
# Quick facts extraction
# =========================================================
def extract_quick_facts(analysis: str) -> Dict[str, str]:
    facts: Dict[str, str] = {}
    lower = analysis.lower()

    if "toxic" in lower:
        facts["Safety"] = "Pet Safe ✅" if any(t in lower for t in ["not toxic", "non-toxic", "non toxic", "safe for pets"]) else "Toxic ⚠️"

    for k, v in {
        "full sun": "☀️ Full Sun",
        "partial shade": "⛅ Partial",
        "full shade": "🌙 Shade",
        "bright indirect": "💡 Bright",
        "low light": "🔅 Low Light",
    }.items():
        if k in lower:
            facts["Light"] = v
            break

    for k, v in {
        "daily": "💧 Daily",
        "weekly": "💦 Weekly",
        "moderate": "💧 Moderate",
        "drought": "🌵 Minimal",
    }.items():
        if k in lower:
            facts["Water"] = v
            break

    return facts


# =========================================================
# Main renderer with support for uploaded images
# =========================================================
def render_plant_analysis_display(
    plant_name: str,
    analysis: str,
    mute_audio: bool = True,
    particles: bool = True,
    allow_model_html: bool = True,
    show_header: bool = False,
    uploaded_image_bytes: Optional[bytes] = None,
) -> None:
    """
    Left: image + quick facts (+ optional audio).
    Right: show LLM output exactly as provided.
    """
    # Render beautiful particles (single stunning effect)
    render_particles(enabled=particles)

    # Only render the big gradient header if explicitly requested
    if show_header:
        render_header()

    st.html(f'<div class="bar-title">🌱 Analysis: {_html.escape(plant_name)}</div>')

    left, right = st.columns([2, 3], gap="large")

    with left:
        # Use uploaded image if provided, otherwise search for one
        if uploaded_image_bytes:
            st.image(uploaded_image_bytes, caption=f"🌿 {plant_name} - User's Image", width='stretch')
        else:
            img = get_plant_image_info(plant_name)
            cap = f"🌿 {plant_name}"
            if img.get("page_url"):
                cap += f" • [{img['caption']}]({img['page_url']})"
            else:
                cap += f" • {img['caption']}"
            st.image(img["url"], caption=cap, width='stretch')

        st.markdown("#### ⭐ Quick Facts")
        facts = extract_quick_facts(analysis)
        if facts:
            cols = st.columns(2)
            for i, (label, value) in enumerate(facts.items()):
                with cols[i % 2]:
                    st.metric(label=label, value=value)

        if not mute_audio:
            st.markdown("#### 🔊 Audio Guide")
            with st.spinner("Generating audio..."):
                try:
                    clean = re.sub(r"\s+", " ", analysis).strip()
                    data = BytesIO()
                    gTTS(text=clean, lang="en").write_to_fp(data)
                    st.audio(data, format="audio/mpeg")
                except Exception as e:
                    st.warning(f"Audio unavailable: {e}")

    with right:
        st.markdown("#### 📋 Detailed Information")
        if allow_model_html:
            st.markdown(analysis, unsafe_allow_html=True)
        else:
            st.markdown(analysis)


# =========================================================
# Public helpers
# =========================================================
def render_custom_css() -> None:
    load_custom_css()


def render_legal_footer() -> None:
    st.html(
        """
        <div style="margin-top:2rem;padding:1.2rem;text-align:center;border-radius:16px;
             background:linear-gradient(135deg,#1e293b,#334155);color:#fff;">
          <div>🌿 Plant Facts Explorer • Version 8.1.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)