"""
UI Components Module
Verbatim LLM rendering + animations (leaf, sheen, typewriter), reliable images
Author: Maniwar
Version: 7.0.0 - Mobile-optimized, single stunning particle effect, streaming animations
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
            padding: 1.5rem 1rem; 
            border-radius: var(--panel-radius);
            color:#fff; 
            box-shadow:0 16px 36px rgba(0,0,0,.15); 
            margin-bottom: 1rem;
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

          /* Typewriter subtitle - Mobile Optimized */
          .subtitle { 
            margin:.45rem 0 0 0; 
            font-size: clamp(0.85rem, 3vw, 1rem);
          }
          
          .typewriter {
            display:inline-block; 
            overflow:hidden; 
            white-space:nowrap;
            border-right:.12em solid rgba(255,255,255,.85);
            animation: typing 3s steps(40,end), blink .85s step-end infinite;
            max-width:100%;
            opacity:.95;
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
              padding: 1.2rem 0.8rem;
            }
            
            .title-row {
              gap: 0.4rem;
            }
            
            .leaf {
              font-size: 1.5rem;
            }
            
            .subtitle {
              margin-top: 0.3rem;
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
    show_leaf: bool = True,
    typewriter: bool = True,
) -> None:
    """Render header with mobile-optimized layout"""
    leaf = '<span class="leaf">🌿</span>' if show_leaf else ""
    sub_html = (
        f'<div class="subtitle"><span class="typewriter">{_html.escape(subtitle)}</span></div>'
        if typewriter
        else f'<div class="subtitle" style="opacity:.95;">{_html.escape(subtitle)}</div>'
    )
    st.html(
        f"""
        <div class="header">
          <div class="sheen"></div>
          <div class="title-row">
            {leaf}
            <div class="headline">Plant Facts Explorer</div>
          </div>
          {sub_html}
        </div>
        """
    )


# =========================================================
# Single Stunning Particle Effect - Magical Garden
# =========================================================
def render_particles(
    enabled: bool = True,
    height: int = 120,
) -> None:
    """
    Single stunning particle effect: Magical Garden
    Combines multiple natural elements for a beautiful, cohesive effect
    """
    if not enabled:
        return

    from streamlit.components.v1 import html as _html_iframe
    
    # Use a simpler, more reliable approach with CSS animations
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
            
            /* Floating light orbs */
            .orb {
                position: absolute;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, 
                    rgba(255, 255, 255, 0.3), 
                    rgba(147, 197, 253, 0.2),
                    transparent);
                filter: blur(1px);
                animation: float-orb 20s infinite ease-in-out;
            }
            
            .orb:nth-child(1) {
                width: 80px; height: 80px;
                left: 10%; top: 20%;
                animation-duration: 18s;
                animation-delay: 0s;
            }
            
            .orb:nth-child(2) {
                width: 60px; height: 60px;
                left: 70%; top: 40%;
                animation-duration: 22s;
                animation-delay: 2s;
            }
            
            .orb:nth-child(3) {
                width: 100px; height: 100px;
                left: 40%; top: 60%;
                animation-duration: 25s;
                animation-delay: 4s;
            }
            
            .orb:nth-child(4) {
                width: 50px; height: 50px;
                left: 85%; top: 15%;
                animation-duration: 20s;
                animation-delay: 1s;
            }
            
            .orb:nth-child(5) {
                width: 70px; height: 70px;
                left: 25%; top: 75%;
                animation-duration: 23s;
                animation-delay: 3s;
            }
            
            /* Falling leaves */
            .leaf {
                position: absolute;
                font-size: 20px;
                animation: fall-leaf 12s infinite linear;
                opacity: 0;
            }
            
            .leaf:nth-child(6) {
                left: 10%;
                animation-delay: 0s;
                animation-duration: 11s;
            }
            
            .leaf:nth-child(7) {
                left: 30%;
                animation-delay: 2s;
                animation-duration: 13s;
            }
            
            .leaf:nth-child(8) {
                left: 50%;
                animation-delay: 4s;
                animation-duration: 10s;
            }
            
            .leaf:nth-child(9) {
                left: 70%;
                animation-delay: 1s;
                animation-duration: 12s;
            }
            
            .leaf:nth-child(10) {
                left: 90%;
                animation-delay: 3s;
                animation-duration: 14s;
            }
            
            /* Floating petals */
            .petal {
                position: absolute;
                width: 15px;
                height: 15px;
                background: radial-gradient(ellipse, 
                    rgba(255, 182, 193, 0.8), 
                    rgba(255, 105, 180, 0.4));
                border-radius: 0 100% 0 100%;
                animation: fall-petal 15s infinite ease-in-out;
                opacity: 0;
            }
            
            .petal:nth-child(11) {
                left: 15%;
                animation-delay: 0.5s;
                animation-duration: 14s;
            }
            
            .petal:nth-child(12) {
                left: 35%;
                animation-delay: 2.5s;
                animation-duration: 16s;
            }
            
            .petal:nth-child(13) {
                left: 55%;
                animation-delay: 1.5s;
                animation-duration: 13s;
            }
            
            .petal:nth-child(14) {
                left: 75%;
                animation-delay: 3.5s;
                animation-duration: 15s;
            }
            
            .petal:nth-child(15) {
                left: 95%;
                animation-delay: 4.5s;
                animation-duration: 17s;
            }
            
            /* Glowing particles */
            .glow {
                position: absolute;
                width: 4px;
                height: 4px;
                background: rgba(255, 255, 200, 0.8);
                border-radius: 50%;
                box-shadow: 0 0 10px rgba(255, 255, 200, 0.5);
                animation: float-glow 20s infinite ease-in-out;
                opacity: 0;
            }
            
            .glow:nth-child(16) {
                left: 20%;
                animation-delay: 0s;
                animation-duration: 18s;
            }
            
            .glow:nth-child(17) {
                left: 40%;
                animation-delay: 1s;
                animation-duration: 19s;
            }
            
            .glow:nth-child(18) {
                left: 60%;
                animation-delay: 2s;
                animation-duration: 21s;
            }
            
            .glow:nth-child(19) {
                left: 80%;
                animation-delay: 3s;
                animation-duration: 20s;
            }
            
            .glow:nth-child(20) {
                left: 45%;
                animation-delay: 4s;
                animation-duration: 22s;
            }
            
            /* Animations */
            @keyframes float-orb {
                0%, 100% {
                    transform: translate(0, 0) scale(1);
                    opacity: 0.3;
                }
                25% {
                    transform: translate(30px, -20px) scale(1.1);
                    opacity: 0.4;
                }
                50% {
                    transform: translate(-20px, 10px) scale(0.95);
                    opacity: 0.3;
                }
                75% {
                    transform: translate(10px, -30px) scale(1.05);
                    opacity: 0.35;
                }
            }
            
            @keyframes fall-leaf {
                0% {
                    transform: translateY(-20px) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 0.7;
                }
                90% {
                    opacity: 0.7;
                }
                100% {
                    transform: translateY(calc(100vh + 20px)) rotate(360deg);
                    opacity: 0;
                }
            }
            
            @keyframes fall-petal {
                0% {
                    transform: translateY(-20px) translateX(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 0.6;
                }
                25% {
                    transform: translateY(25vh) translateX(20px) rotate(90deg);
                }
                50% {
                    transform: translateY(50vh) translateX(-15px) rotate(180deg);
                }
                75% {
                    transform: translateY(75vh) translateX(25px) rotate(270deg);
                }
                90% {
                    opacity: 0.6;
                }
                100% {
                    transform: translateY(calc(100vh + 20px)) translateX(0) rotate(360deg);
                    opacity: 0;
                }
            }
            
            @keyframes float-glow {
                0%, 100% {
                    transform: translateY(0) translateX(0);
                    opacity: 0;
                }
                10% {
                    opacity: 0.8;
                }
                50% {
                    transform: translateY(-30px) translateX(20px);
                    opacity: 0.4;
                }
                90% {
                    opacity: 0.8;
                }
            }
            
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .orb, .leaf, .petal, .glow {
                    animation: none !important;
                    opacity: 0.3;
                }
            }
        </style>
    </head>
    <body>
        <div class="particle-container">
            <!-- Light orbs -->
            <div class="orb"></div>
            <div class="orb"></div>
            <div class="orb"></div>
            <div class="orb"></div>
            <div class="orb"></div>
            
            <!-- Falling leaves -->
            <div class="leaf">🍃</div>
            <div class="leaf">🍃</div>
            <div class="leaf">🍃</div>
            <div class="leaf">🍃</div>
            <div class="leaf">🍃</div>
            
            <!-- Floating petals -->
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            
            <!-- Glowing particles -->
            <div class="glow"></div>
            <div class="glow"></div>
            <div class="glow"></div>
            <div class="glow"></div>
            <div class="glow"></div>
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
    floating_leaf: bool = True,
    typewriter_subtitle: bool = True,
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
        render_header(show_leaf=floating_leaf, typewriter=typewriter_subtitle)

    st.html(f'<div class="bar-title">🌱 Analysis: {_html.escape(plant_name)}</div>')

    left, right = st.columns([2, 3], gap="large")

    with left:
        # Use uploaded image if provided, otherwise search for one
        if uploaded_image_bytes:
            st.image(uploaded_image_bytes, caption=f"🌿 {plant_name} - User's Image", use_container_width=True)
        else:
            img = get_plant_image_info(plant_name)
            cap = f"🌿 {plant_name}"
            if img.get("page_url"):
                cap += f" • [{img['caption']}]({img['page_url']})"
            else:
                cap += f" • {img['caption']}"
            st.image(img["url"], caption=cap, use_container_width=True)

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
          <div>🌿 Plant Facts Explorer • Version 7.0.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)