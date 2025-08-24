"""
UI Components Module
Clean layout, reliable images, minimal formatting
Author: Maniwar
Version: 3.0.0 - Simple & Beautiful
"""

import re
from io import BytesIO
from typing import Dict, Optional
from urllib.parse import quote

import requests
import streamlit as st
from gtts import gTTS


# =========================
# Global CSS
# =========================
def load_custom_css():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

            .stApp { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

            .header-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2.25rem 1.75rem; border-radius: 20px; margin-bottom: 1.25rem;
                color: white; box-shadow: 0 16px 36px rgba(0,0,0,.15);
            }
            .header-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin: 0; }
            .header-sub { opacity:.95; margin:.5rem 0 0 0 }

            .bar-title {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; font-weight: 700; padding: .9rem 1rem; border-radius: 12px;
                display:flex; align-items:center; gap:.6rem; margin-top:.5rem;
            }

            /* Image niceties */
            .stImage { border-radius: 14px; box-shadow: 0 8px 24px rgba(0,0,0,.12); }

            /* Section label pills (tiny) */
            .pill { display:inline-flex; align-items:center; gap:.5rem; font-weight:700;
                    border:1px solid rgba(148,163,184,.35); padding:.35rem .6rem; border-radius:999px;
                    background: rgba(102,126,234,.12); margin:.5rem 0 .4rem 0; }

            /* Quick facts metrics spacing */
            [data-testid="metric-container"] { border-radius: 14px; padding: 1.1rem; }

            /* Clean lists spacing */
            .stMarkdown ul { margin-top:.2rem; }
            .stMarkdown p:empty, span:empty, div[data-testid="stMarkdownContainer"] > p:empty { display:none!important; }

            /* Footer */
            .footer-container { margin-top: 3rem; padding: 2rem; text-align:center;
                border-radius: 16px; background: linear-gradient(135deg, #1e293b, #334155); color:white; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="header-container">
          <div class="header-title">Plant Facts Explorer</div>
          <div class="header-sub">Discover the amazing world of plants with AI-powered insights</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Wikipedia image resolver (cached)
# =========================
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
        if r.status_code == 200:
            hits = r.json().get("query", {}).get("search", [])
            if hits:
                return hits[0]["title"]
    except Exception:
        pass
    return None


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
    """Return {'url','caption','page_url'} using Wikipedia; neutral placeholder otherwise."""
    title = _normalize_plant_title(plant_name)
    js = _wiki_summary(title) or (_wiki_summary(_wiki_search(title)) if _wiki_search(title) else None)

    if js:
        img = (js.get("thumbnail") or {}).get("source") or (js.get("originalimage") or {}).get("source")
        if img:
            page = (js.get("content_urls") or {}).get("desktop", {}).get("page")
            return {"url": img, "caption": f"🔗 Wikipedia: {js.get('title')}", "page_url": page}

    seed = quote(plant_name.lower())
    return {"url": f"https://picsum.photos/seed/{seed}/800/600", "caption": f"Placeholder image", "page_url": None}


# Back-compat
def get_plant_image_url(plant_name: str) -> str:
    return get_plant_image_info(plant_name)["url"]


# =========================
# Quick facts + analysis cleaning
# =========================
def extract_quick_facts(analysis: str) -> Dict[str, str]:
    facts: Dict[str, str] = {}
    lower = analysis.lower()

    # Toxicity
    if "toxic" in lower:
        facts["Safety"] = "Pet Safe ✅" if any(t in lower for t in ["not toxic", "non-toxic", "non toxic"]) else "Toxic ⚠️"

    # Light
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

    # Water
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


# --- The simplest approach: flatten and prettify ---
_HEADING_WORDS = [
    "overview",
    "general information",
    "care instructions",
    "toxicity",
    "propagation",
    "common issues",
    "interesting facts",
]

_EMOJI_BULLETS = r"[\-\*\u2022●◦▪️▫️■□☑️✅➤▶️►▸▹▻▪︎▫︎🔹🔸⭐️✨💡📌📝🌱⚠️🌿🐛🔧🔬🎯]"


def _clean_report_text(md: str) -> str:
    """
    Make the LLM report read cleanly:
      - remove big/duplicate headings (##, ###, '1. Title', etc.)
      - convert label lines into neat bullets: '• **Label:** value'
      - keep real lists as they are
    """
    text = md.strip()

    # 1) Remove giant title blocks (H1/H2) and leading "Comprehensive Report ..." line
    text = re.sub(r"^\s*#{1,3}\s+.*\n?", "", text, flags=re.MULTILINE)

    # 2) Drop standalone section headers like "1. General Information:" / "General Information:"
    for w in _HEADING_WORDS:
        text = re.sub(rf"^\s*(?:\d+\s*[\.\)]\s*)?{w}\s*:\s*$", "", text, flags=re.IGNORECASE | re.MULTILINE)

    # 3) Turn label lines into bullets: '**Label:** value'  or '**Label**: value'
    def bulletize(m):
        label = m.group(1).strip()
        val = (m.group(2) or "").strip()
        if not label.endswith(":"):
            label += ":"
        if val:
            return f"- **{label}** {val}"
        return f"- **{label}**"

    # a) "**Label:** value"
    text = re.sub(r"^\s*\*\*\s*([^*\n]+?)\s*\*\*\s*:\s*(.+)$", bulletize, text, flags=re.MULTILINE)
    # b) "**Label**: value"
    text = re.sub(r"^\s*\*\*\s*([^*\n]+?)\s*\*\*\s*\:\s*(.+)$", bulletize, text, flags=re.MULTILINE)
    # c) "Label: value" (avoid list items)
    text = re.sub(r"^(?!\s*[-*]\s)([A-Z][A-Za-z0-9 \-/]{2,30})\s*:\s*(.+)$", bulletize, text, flags=re.MULTILINE)

    # 4) Normalize stray heading lines (##/###/emoji+bold) -> remove
    text = re.sub(r"^\s*#{2,6}\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(rf"^\s*{_EMOJI_BULLETS}\s*\*\*.*\*\*\s*$", "", text, flags=re.MULTILINE)

    # 5) Clean empty clutter + compact spacing
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


# =========================
# Main renderer (simple)
# =========================
def render_plant_analysis_display(plant_name: str, analysis: str, mute_audio: bool = True):
    with st.container():
        # Bar title
        st.markdown(f'<div class="bar-title">🌱 Analysis: {plant_name}</div>', unsafe_allow_html=True)

        # Two columns
        col1, col2 = st.columns([2, 3], gap="large")

        with col1:
            # Image + attribution
            img = get_plant_image_info(plant_name)
            cap = f"🌿 {plant_name}"
            if img.get("page_url"):
                cap += f" • [{img['caption']}]({img['page_url']})"
            else:
                cap += f" • {img['caption']}"
            st.image(img["url"], caption=cap, use_container_width=True)

            # Quick Facts
            st.markdown("#### ⭐ Quick Facts")
            facts = extract_quick_facts(analysis)
            if facts:
                fc = st.columns(2)
                i = 0
                for label, value in facts.items():
                    with fc[i % 2]:
                        st.metric(label=label, value=value)
                    i += 1

            if not mute_audio:
                st.markdown("#### 🔊 Audio Guide")
                with st.spinner("Generating audio..."):
                    try:
                        cleaned = re.sub(r"\s+", " ", analysis)
                        b = BytesIO(); gTTS(text=cleaned, lang="en").write_to_fp(b)
                        st.audio(b, format="audio/mpeg")
                    except Exception as e:
                        st.warning(f"Audio unavailable: {e}")

        with col2:
            st.markdown("#### 📋 Detailed Information")
            # Tiny context pill if we detect a top report line
            if "report" in analysis.lower():
                st.markdown('<span class="pill">📌 Overview</span>', unsafe_allow_html=True)

            clean_body = _clean_report_text(analysis)
            st.markdown(clean_body)


# =========================
# Public helpers
# =========================
def render_custom_css():
    load_custom_css()


def render_legal_footer():
    st.markdown(
        """
        <div class="footer-container">
            <div>🌿 Plant Facts Explorer • Version 3.0.0</div>
            <div style="opacity:.8; font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backwards compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)
