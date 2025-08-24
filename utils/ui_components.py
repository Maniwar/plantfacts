"""
UI Components Module
Verbatim LLM rendering + animations (leaf, sheen, typewriter), reliable images
Author: Maniwar
Version: 5.1.0
"""

from __future__ import annotations

import html as _html
import re
from io import BytesIO
from typing import Dict, Optional
from urllib.parse import quote

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
# Optional particle background (JS in iframe)
# =========================================================
def render_particles(
    enabled: bool = False,
    height: int = 320,
    preset: str = "aurora",   # "aurora" | "constellation" | "leaves"
    watermark_text: str = "AI Analysis",
    watermark_opacity: float = 0.12,
    intensity: float = 1.0,   # 0.5..1.5 scales motion/quantity
    show_watermark: bool = True,
) -> None:
    """
    Fancy particle backgrounds using tsParticles with three presets.
    - No Streamlit 'key' needed; safe for older versions.
    - Pointer-events disabled; does not block UI.
    """
    if not enabled:
        return

    from streamlit.components.v1 import html as _html_iframe
    import json

    # Clamp/sanitize
    preset = (preset or "aurora").lower().strip()
    if preset not in {"aurora", "constellation", "leaves"}:
        preset = "aurora"
    intensity = max(0.4, min(1.6, float(intensity)))
    wm = (watermark_text or "").strip() or "AI Analysis"

    html_code = """
    <!doctype html><html><head><meta charset="utf-8"/>
    <style>
      :root { --wm-opacity: __WM_OPACITY__; }
      html,body,#stage { margin:0; padding:0; height:100%; width:100%; background:transparent; }
      #stage { position:relative; pointer-events:none; }
      #tsp { position:absolute; inset:0; z-index:0; }
      #wm {
        position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
        font: 800 clamp(42px, 16vw, 220px) "Space Grotesk", Inter, system-ui, -apple-system, sans-serif;
        letter-spacing:.04em; color:#fff; opacity:var(--wm-opacity);
        text-shadow:0 4px 18px rgba(0,0,0,.28); z-index:1; white-space:nowrap; user-select:none;
        animation: floatSlow 18s ease-in-out infinite;
      }
      @keyframes floatSlow {
        0%   { transform: translate(-50%,-50%) rotate(0deg); }
        50%  { transform: translate(calc(-50% + 6px), calc(-50% - 6px)) rotate(3deg); }
        100% { transform: translate(-50%,-50%) rotate(0deg); }
      }
      @media (prefers-reduced-motion: reduce) { #wm { animation:none; } }
    </style>
    </head><body>
      <div id="stage">
        <div id="tsp"></div>
        <div id="wm" style="display: __WM_DISPLAY__;">__WM_TEXT__</div>
      </div>

      <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.12.0/tsparticles.bundle.min.js"></script>
      <script>
        (async () => {
          const engine = window.tsParticles;
          const PRESET = "__PRESET__";
          const INTENSITY = __INTENSITY__;   // scales counts & speeds

          // Base colors
          const palette = ["#a7f3d0","#93c5fd","#c4b5fd","#fde68a"];

          // Build config per preset
          let config = {
            detectRetina: true,
            fullScreen: { enable: false },
            background: { color: { value: "transparent" } },
            fpsLimit: 60,
            particles: {},
            interactivity: {
              events: { resize: true },
              modes: {}
            }
          };

          if (PRESET === "aurora") {
            // Flowing ribbons using trails + curved motion
            config.particles = {
              number: { value: Math.round(18 * INTENSITY), density: { enable: true, area: 800 } },
              color: { value: palette },
              opacity: { value: 0.22 },
              size: { value: { min: 1, max: 3 } },
              move: {
                enable: true,
                speed: 0.55 * INTENSITY,
                direction: "none",
                random: true,
                straight: false,
                outModes: { default: "out" },
                trail: { enable: true, length: Math.round(14 * INTENSITY), fill: { color: "transparent" } }
              },
              links: { enable: false }
            };
            config.interactivity.events.onHover = { enable: true, mode: "attract" };
            config.interactivity.modes.attract = { distance: 160, duration: 0.4 };

          } else if (PRESET === "constellation") {
            // Dense starfield with twinkling links
            config.particles = {
              number: { value: Math.round(70 * INTENSITY), density: { enable: true, area: 800 } },
              color: { value: "#e5f0ff" },
              opacity: { value: { min: 0.15, max: 0.55 }, animation: { enable: true, speed: 0.6, sync: false } },
              size: { value: { min: 1, max: 2.6 } },
              move: { enable: true, speed: 0.45 * INTENSITY, outModes: { default: "out" } },
              links: { enable: true, distance: 140, opacity: 0.18, color: "#bcd1ff" }
            };
            config.interactivity.events.onHover = { enable: true, mode: "repulse" };
            config.interactivity.modes.repulse = { distance: 120, duration: 0.3 };

          } else if (PRESET === "leaves") {
            // Drifting leaf glyphs (emoji + simple shapes)
            config.particles = {
              number: { value: Math.round(22 * INTENSITY), density: { enable: true, area: 800 } },
              color: { value: ["#8ee59b","#6ee7b7","#a3e635", "#86efac"] },
              opacity: { value: 0.28 },
              size: { value: { min: 6, max: 12 } },
              shape: {
                type: ["character","circle"],
                options: {
                  character: [{
                    value: "🍃",
                    font: "Segoe UI Emoji",
                    style: "",
                    weight: "400"
                  }]
                }
              },
              move: {
                enable: true,
                speed: 0.35 * INTENSITY,
                direction: "bottom",
                outModes: { default: "out" },
                drift: 0.6,
                angle: { offset: 20, value: 40 },
                gravity: { enable: false }
              },
              rotate: { value: { min: 0, max: 360 }, direction: "random", animation: { enable: true, speed: 6 } },
              links: { enable: false }
            };
          }

          await engine.load("tsp", config);
        })();
      </script>
    </body></html>
    """

    _html_iframe(
        html_code
          .replace("__PRESET__", preset)
          .replace("__INTENSITY__", json.dumps(float(intensity)))
          .replace("__WM_TEXT__", (wm if show_watermark else ""))
          .replace("__WM_DISPLAY__", "block" if show_watermark else "none")
          .replace("__WM_OPACITY__", str(watermark_opacity)),
        height=height,
        scrolling=False,
    )

# =========================================================
# Wikipedia image resolver (cached)
# =========================================================
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
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


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def _wiki_search(query: str) -> Optional[str]:
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": f'{query} incategory:"Plants" OR incategory:"Flora"',
                "utf8": 1,
                "format": "json",
                "srlimit": 5,
            },
            timeout=6,
        )
    except Exception:
        return None
    if r.status_code != 200:
        return None
    hits = r.json().get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


def _normalize_plant_title(name: str) -> str:
    key = name.strip().lower()
    return {
        "tulip tree": "Liriodendron tulipifera",
        "yellow poplar": "Liriodendron tulipifera",
        "snake plant": "Dracaena trifasciata",
        "spider plant": "Chlorophytum comosum",
        "pothos": "Epipremnum aureum",
        "money plant": "Epipremnum aureum",
        "peace lily": "Spathiphyllum",
        "rubber plant": "Ficus elastica",
        "rubber tree": "Ficus elastica",
        "zz plant": "Zamioculcas",
    }.get(key, name.strip())


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_info(plant_name: str) -> Dict[str, Optional[str]]:
    title = _normalize_plant_title(plant_name)
    js = _wiki_summary(title)
    if not js:
        found = _wiki_search(title)
        if found:
            js = _wiki_summary(found)

    if js:
        img = (js.get("thumbnail") or {}).get("source") or (js.get("originalimage") or {}).get("source")
        if img:
            page = (js.get("content_urls") or {}).get("desktop", {}).get("page")
            return {"url": img, "caption": f"🔗 Wikipedia: {js.get('title')}", "page_url": page}

    seed = quote(plant_name.lower())
    return {"url": f"https://picsum.photos/seed/{seed}/800/600", "caption": "Placeholder image", "page_url": None}


def get_plant_image_url(plant_name: str) -> str:  # backward compatibility
    return get_plant_image_info(plant_name)["url"]


# =========================================================
# Quick facts (lightweight heuristics)
# =========================================================
def extract_quick_facts(analysis: str) -> Dict[str, str]:
    facts: Dict[str, str] = {}
    lower = analysis.lower()

    if "toxic" in lower:
        facts["Safety"] = "Pet Safe ✅" if any(t in lower for t in ["not toxic", "non-toxic", "non toxic"]) else "Toxic ⚠️"

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
# Main renderer — VERBATIM right pane
# =========================================================
def render_plant_analysis_display(
    plant_name: str,
    analysis: str,
    mute_audio: bool = True,
    particles: bool = True,
    floating_leaf: bool = True,
    typewriter_subtitle: bool = True,
    allow_model_html: bool = True,   # set True if you trust model HTML
    show_header: bool = False,       # <-- default False to avoid duplicate header
) -> None:
    """
    Left: image + quick facts (+ optional audio).
    Right: show LLM output exactly as provided.
    """
    # Optional background particles (safe to call multiple times; draws in an iframe)
    render_particles(enabled=particles)

    # Only render the big gradient header if explicitly requested
    if show_header:
        render_header(show_leaf=floating_leaf, typewriter=typewriter_subtitle)

    st.html(f'<div class="bar-title">🌱 Analysis: {_html.escape(plant_name)}</div>')

    left, right = st.columns([2, 3], gap="large")

    with left:
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
            st.markdown(analysis, unsafe_allow_html=True)  # raw HTML allowed
        else:
            st.markdown(analysis)  # Markdown only (safer)



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
          <div>🌿 Plant Facts Explorer • Version 5.1.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)
