"""
UI Components Module
Verbatim LLM rendering + animations (leaf, sheen, typewriter), reliable images
Author: Maniwar
Version: 5.2.0 - Fixed particles, improved image handling
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
# Global CSS (only our own HTML is passed here)
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

          /* Header */
          .header {
            position:relative; overflow:hidden;
            background:linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 100%);
            padding: 2.1rem 1.6rem; border-radius: var(--panel-radius);
            color:#fff; box-shadow:0 16px 36px rgba(0,0,0,.15); margin-bottom: 1rem;
          }
          .sheen { position:absolute; top:-50%; right:-10%; width:60%; height:200%;
                   background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
                   animation: shimmer 3.5s ease-in-out infinite; pointer-events:none; }
          .title-row { display:flex; align-items:center; gap:.75rem; }
          .leaf { font-size:2rem; filter: drop-shadow(0 8px 16px rgba(0,0,0,.25));
                  animation: float 4.5s ease-in-out infinite; }
          .headline { font-family:'Space Grotesk', sans-serif; font-size:2rem; font-weight:700; line-height:1.1; margin:0; }

          /* Typewriter subtitle */
          .subtitle { margin:.45rem 0 0 0; }
          .typewriter {
            display:inline-block; overflow:hidden; white-space:nowrap;
            border-right:.12em solid rgba(255,255,255,.85);
            animation: typing 3s steps(40,end), blink .85s step-end infinite;
            max-width:100%;
            opacity:.95;
          }

          .bar-title {
            background:linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 100%);
            color:#fff; font-weight:700; padding:.8rem 1rem; border-radius:12px;
            display:flex; align-items:center; gap:.6rem; margin-top:.3rem;
          }

          .stImage { border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,.12); }

          /* Animations */
          @keyframes shimmer { 0%,100%{transform:translateX(0)} 50%{transform:translateX(18px)} }
          @keyframes float   { 0%,100%{transform:translateY(0) rotate(0deg)} 50%{transform:translateY(-10px) rotate(6deg)} }
          @keyframes typing  { from{ width:0 } to{ width:100% } }
          @keyframes blink   { from, to { border-color: transparent } 50% { border-color: rgba(255,255,255,.85) } }

          /* Respect reduced motion */
          @media (prefers-reduced-motion: reduce) {
            .sheen, .leaf, .typewriter { animation: none !important; border-right:none; }
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
# Fixed particle background with stable performance
# =========================================================
def render_particles(
    enabled: bool = False,
    height: int = 100,
    preset: str = "leaves",
    watermark_text: str = "AI Analysis",
    watermark_opacity: float = 0.12,
    intensity: float = 1.0,
    show_watermark: bool = True,
) -> None:
    """
    Fixed particle backgrounds with stable performance.
    Prevents speed accumulation and ensures smooth animations.
    """
    if not enabled:
        return

    from streamlit.components.v1 import html as _html_iframe
    import json

    # Generate unique container ID to prevent accumulation
    container_id = f"tsp_{hash(str(st.session_state.get('particle_refresh', 0))) % 10000}"
    
    # Clamp/sanitize
    preset = (preset or "leaves").lower().strip()
    if preset not in {"aurora", "constellation", "leaves"}:
        preset = "leaves"
    intensity = max(0.5, min(1.5, float(intensity)))
    wm = (watermark_text or "").strip() or "AI Analysis"

    # Font sizing based on height
    if height <= 120:
        font_css = '600 clamp(12px, 4vw, 32px)'
    elif height <= 200:
        font_css = '700 clamp(16px, 5vw, 48px)'
    else:
        font_css = '800 clamp(24px, 8vw, 96px)'

    html_code = f"""
    <!doctype html><html><head><meta charset="utf-8"/>
    <style>
      :root {{ --wm-opacity: {watermark_opacity}; }}
      html,body,#stage {{ margin:0; padding:0; height:100%; width:100%; background:transparent; overflow:hidden; }}
      #stage {{ position:relative; pointer-events:none; }}
      #{container_id} {{ position:absolute; inset:0; z-index:0; }}
      #wm {{
        position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
        font: {font_css} "Space Grotesk", Inter, system-ui, -apple-system, sans-serif;
        letter-spacing:.03em; color:#fff; opacity:var(--wm-opacity);
        text-shadow:0 2px 8px rgba(0,0,0,.25); z-index:1; white-space:nowrap; user-select:none;
        animation: floatSlow 18s ease-in-out infinite;
      }}
      @keyframes floatSlow {{
        0%, 100% {{ transform: translate(-50%,-50%) rotate(0deg); }}
        50% {{ transform: translate(calc(-50% + 6px), calc(-50% - 6px)) rotate(3deg); }}
      }}
      @media (prefers-reduced-motion: reduce) {{ #wm {{ animation:none; }} }}
    </style>
    </head><body>
      <div id="stage">
        <div id="{container_id}"></div>
        {'<div id="wm">' + _html.escape(wm) + '</div>' if show_watermark else ''}
      </div>

      <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.12.0/tsparticles.bundle.min.js"></script>
      <script>
        (async () => {{
          // Clear any existing instances to prevent accumulation
          if (window.tsParticlesInstance) {{
            window.tsParticlesInstance.destroy();
          }}
          
          const engine = window.tsParticles;
          const PRESET = "{preset}";
          const INTENSITY = {json.dumps(float(intensity))};

          const palette = ["#a7f3d0","#93c5fd","#c4b5fd","#fde68a"];
          let config = {{
            detectRetina: true,
            fullScreen: {{ enable: false }},
            background: {{ color: {{ value: "transparent" }} }},
            fpsLimit: 60,
            particles: {{}},
            interactivity: {{ events: {{ resize: true }}, modes: {{}} }}
          }};

          if (PRESET === "aurora") {{
            config.particles = {{
              number: {{ value: Math.round(15 * INTENSITY), density: {{ enable: true, area: 800 }} }},
              color: {{ value: palette }},
              opacity: {{ value: 0.22 }},
              size: {{ value: {{ min: 1, max: 3 }} }},
              move: {{
                enable: true,
                speed: 0.4 * INTENSITY,
                random: true,
                straight: false,
                outModes: {{ default: "out" }},
                trail: {{ enable: true, length: Math.round(10 * INTENSITY), fill: {{ color: "transparent" }} }}
              }},
              links: {{ enable: false }}
            }};
            config.interactivity.events.onHover = {{ enable: false }};
          }} 
          else if (PRESET === "constellation") {{
            config.particles = {{
              number: {{ value: Math.round(50 * INTENSITY), density: {{ enable: true, area: 800 }} }},
              color: {{ value: "#e5f0ff" }},
              opacity: {{ value: {{ min: 0.15, max: 0.55 }}, animation: {{ enable: true, speed: 0.5, sync: false }} }},
              size: {{ value: {{ min: 1, max: 2.5 }} }},
              move: {{ 
                enable: true, 
                speed: 0.3 * INTENSITY, 
                direction: "none",
                random: false,
                straight: false,
                outModes: {{ default: "out" }} 
              }},
              links: {{ 
                enable: true, 
                distance: 140, 
                opacity: 0.18, 
                color: "#bcd1ff",
                width: 1
              }}
            }};
            config.interactivity.events.onHover = {{ enable: false }};
          }} 
          else if (PRESET === "leaves") {{
            config.particles = {{
              number: {{ value: Math.round(18 * INTENSITY), density: {{ enable: true, area: 800 }} }},
              color: {{ value: ["#8ee59b","#6ee7b7","#a3e635", "#86efac"] }},
              opacity: {{ value: 0.35 }},
              size: {{ value: {{ min: 8, max: 14 }} }},
              shape: {{
                type: ["character"],
                options: {{ character: [{{ value: "🍃", font: "Segoe UI Emoji" }}] }}
              }},
              move: {{
                enable: true,
                speed: 0.8 * INTENSITY,
                direction: "bottom-right",
                random: false,
                straight: false,
                outModes: {{ default: "out" }},
                gravity: {{ enable: true, acceleration: 0.5 }}
              }},
              rotate: {{ 
                value: {{ min: 0, max: 360 }}, 
                direction: "random",
                animation: {{ enable: true, speed: 5, sync: false }} 
              }},
              wobble: {{ enable: true, distance: 10, speed: 10 }},
              links: {{ enable: false }}
            }};
          }}

          // Store instance globally for cleanup
          window.tsParticlesInstance = await engine.load("{container_id}", config);
        }})();
      </script>
    </body></html>
    """

    _html_iframe(html_code, height=height, scrolling=False)


# =========================================================
# Improved Plant Image Service with multiple sources
# =========================================================
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_from_pexels(plant_name: str) -> Optional[Dict[str, str]]:
    """Try to get plant image from Pexels API (requires API key in secrets)"""
    try:
        # Check if Pexels API key is available
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
        # Search for species
        search_response = requests.get(
            f"https://api.gbif.org/v1/species/match?name={quote(plant_name)}",
            timeout=5
        )
        if search_response.status_code == 200:
            species_data = search_response.json()
            if species_data.get("usageKey"):
                # Get media for this species
                media_response = requests.get(
                    f"https://api.gbif.org/v1/species/{species_data['usageKey']}/media",
                    timeout=5
                )
                if media_response.status_code == 200:
                    media_data = media_response.json()
                    results = media_data.get("results", [])
                    # Filter for images
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
        # Try direct title
        title = _normalize_plant_title(plant_name)
        js = _wiki_summary(title)
        
        # If not found, search with better query
        if not js:
            # Search specifically in plant categories
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
    # Use a deterministic seed based on plant name for consistency
    seed = hashlib.md5(plant_name.encode()).hexdigest()[:10]
    
    # Unsplash public CDN with search terms
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
    """
    Enhanced image fetching with multiple sources and better fallbacks.
    Tries multiple sources in order of preference.
    """
    # Try multiple sources in order
    
    # 1. Try Pexels first (high quality images)
    result = get_plant_image_from_pexels(plant_name)
    if result and result.get("url"):
        return result
    
    # 2. Try GBIF (scientific database)
    result = get_plant_image_from_gbif(plant_name)
    if result and result.get("url"):
        return result
    
    # 3. Try Wikipedia (good for common plants)
    result = get_plant_image_from_wikipedia(plant_name)
    if result and result.get("url"):
        return result
    
    # 4. Use Unsplash as final fallback (always returns something)
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
    uploaded_image_bytes: Optional[bytes] = None,  # New parameter for uploaded/captured images
) -> None:
    """
    Left: image + quick facts (+ optional audio).
    Right: show LLM output exactly as provided.
    
    Args:
        uploaded_image_bytes: If provided, use this image instead of searching for one
    """
    # Optional background particles
    render_particles(enabled=particles, preset="leaves", intensity=1.0)

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
          <div>🌿 Plant Facts Explorer • Version 5.2.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)