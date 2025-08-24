"""
UI Components Module
Reusable UI components with better image handling and improved UX
Author: Maniwar
Version: 2.10.0 - Clean sections: strip duplicate headings, normalize subheaders; Wikipedia images
"""

import re
from io import BytesIO
from typing import Dict, Tuple, Literal, Optional
from urllib.parse import quote

import requests
import streamlit as st
from gtts import gTTS


# =========================
# Global CSS / Theming
# =========================
def load_custom_css():
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

        .stApp { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

        /* Hide empty paragraphs that sometimes appear */
        .stMarkdown p:empty,
        span:empty,
        div[data-testid="stMarkdownContainer"] > p:empty { display: none !important; }

        /* Beautiful header */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem; border-radius: 24px; margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15); position: relative; overflow: hidden;
        }
        .header-container::before {
            content: ''; position: absolute; top: -50%; right: -10%; width: 60%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }
        @keyframes shimmer { 0%,100%{transform:translateX(0)} 50%{transform:translateX(20px)} }
        .header-content { display:flex; align-items:center; color:white; position:relative; z-index:1; }
        .header-icon { font-size:72px; margin-right:24px; filter:drop-shadow(0 10px 20px rgba(0,0,0,0.2)); }
        .header-text h1 { margin:0; font-size:3rem; font-weight:700; font-family:'Space Grotesk',sans-serif; color:white!important; text-shadow:2px 2px 4px rgba(0,0,0,0.2); }
        .header-text p { margin:0.75rem 0 0 0; font-size:1.25rem; opacity:0.95; color:rgba(255,255,255,0.95); }

        /* Analysis header */
        .analysis-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color:white; padding:1.25rem 1rem; border-radius:16px; font-size:1.25rem; font-weight:700;
            display:flex; align-items:center; gap:12px; margin-bottom:0;
        }

        /* Metrics styling */
        [data-testid="metric-container"] {
            background: rgba(255,255,255,0.9); border: 2px solid #e2e8f0; padding: 1.25rem; border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        [data-theme="dark"] [data-testid="metric-container"] {
            background: rgba(30,41,59,0.9); border-color: #475569;
        }

        /* Section header (simple, stable) */
        .section-hdr {
            display:flex; align-items:center; gap:10px;
            padding: .55rem .8rem;
            border: 1px solid rgba(148,163,184,.35);
            background: linear-gradient(135deg, rgba(102,126,234,.12), rgba(118,75,162,.12));
            border-radius: 10px;
            font-weight: 700; margin: .9rem 0 .4rem 0;
            font-family: 'Space Grotesk', sans-serif;
        }

        /* Images */
        .stImage { border-radius: 16px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.12); }

        /* Footer */
        .footer-container {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 3rem; border-radius: 24px; margin-top: 4rem; color: white; text-align: center;
        }

        @media (max-width: 768px) {
            .header-text h1 { font-size:2rem; }
            .header-icon { font-size:48px; }
            .header-container { padding:2rem 1.5rem; }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    st.markdown(
        """
        <div class="header-container">
          <div class="header-content">
            <div class="header-icon">🌿</div>
            <div class="header-text">
              <h1>Plant Facts Explorer</h1>
              <p>Discover the amazing world of plants with AI-powered insights</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Wikipedia image resolver
# =========================
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def _wiki_summary(title: str) -> Optional[dict]:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def _wiki_search(query: str) -> Optional[str]:
    try:
        api = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f'{query} incategory:"Plants" OR incategory:"Flora"',
            "utf8": 1,
            "format": "json",
            "srlimit": 5,
        }
        r = requests.get(api, params=params, timeout=6)
        if r.status_code == 200:
            hits = r.json().get("query", {}).get("search", [])
            if hits:
                return hits[0]["title"]
    except Exception:
        pass
    return None


def _normalize_plant_title(plant_name: str) -> str:
    name = plant_name.strip().lower()
    return {
        "tulip tree": "Liriodendron tulipifera",
        "yellow poplar": "Liriodendron tulipifera",
        "snake plant": "Dracaena trifasciata",
        "mother-in-law's tongue": "Dracaena trifasciata",
        "spider plant": "Chlorophytum comosum",
        "money plant": "Epipremnum aureum",
        "pothos": "Epipremnum aureum",
        "peace lily": "Spathiphyllum",
        "rubber plant": "Ficus elastica",
        "rubber tree": "Ficus elastica",
        "zz plant": "Zamioculcas",
    }.get(name, plant_name.strip())


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def get_plant_image_info(plant_name: str) -> Dict[str, Optional[str]]:
    """
    Resolve a plant image via Wikipedia/Wikimedia with attribution.
    Returns:
      {"url": str, "caption": str, "page_url": Optional[str]}
    """
    title = _normalize_plant_title(plant_name)
    js = _wiki_summary(title)

    if not js or js.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
        found = _wiki_search(title)
        if found:
            js = _wiki_summary(found)

    if js:
        thumb = js.get("thumbnail", {}) or {}
        page = js.get("content_urls", {}).get("desktop", {}).get("page")
        page_title = js.get("title")
        img_url = thumb.get("source") or (js.get("originalimage", {}) or {}).get("source")
        if img_url:
            return {"url": img_url, "caption": f"🔗 Wikipedia: {page_title}", "page_url": page}

    # Neutral placeholder (obviously generic)
    seed = quote(plant_name.lower())
    return {
        "url": f"https://picsum.photos/seed/{seed}/800/600",
        "caption": f"Placeholder image for '{plant_name}'",
        "page_url": None,
    }


def get_plant_image_url(plant_name: str) -> str:
    return get_plant_image_info(plant_name)["url"]


# =========================
# Content helpers
# =========================
def extract_quick_facts(analysis: str) -> Dict[str, str]:
    facts: Dict[str, str] = {}
    lower = analysis.lower()

    # Toxicity
    if "toxic" in lower:
        if ("not toxic" in lower) or ("non-toxic" in lower) or ("non toxic" in lower):
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
        if pattern in lower:
            facts["Light"] = display
            break

    # Water
    for pattern, display in {
        "daily": "💧 Daily",
        "weekly": "💦 Weekly",
        "moderate": "💧 Moderate",
        "drought": "🌵 Minimal",
    }.items():
        if pattern in lower:
            facts["Water"] = display
            break

    # Origin
    m = re.search(r"native to ([^,\.]+)", lower)
    if m:
        facts["Origin"] = f"🌍 {m.group(1).title()}"

    return facts


def clean_text_for_tts(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\#\#(.*?)\n", r"\1. ", text)
    text = re.sub(r"\#(.*?)\n", r"\1. ", text)
    text = re.sub(r"\* (.*?)\n", r"\1. ", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = text.replace("|", ", ").replace("-", " ").replace("`", "")
    return text


# ---------- Normalizers for section bodies ----------
_HEADING_WORDS = [
    "overview",
    "general information",
    "care instructions",
    "toxicity",
    "propagation",
    "common issues",
    "problems",
    "interesting facts",
]

_EMOJI_BULLETS = r"[\-\*\u2022●◦▪️▫️■□☑️✅➤▶️►▸▹▻▪︎▫︎🔹🔸⭐️✨💡📌📝🌱⚠️🌿🐛🔧🔬🎯]"


def _strip_leading_section_line(text: str, title: str) -> str:
    """
    Remove a first line like '1. General Information:' or 'General Information:' (case-insensitive).
    """
    lines = text.splitlines()
    if not lines:
        return text
    first = lines[0].strip().lower().rstrip(".:")
    t = title.strip().lower()
    # matches "1. Title", "Title", "1 Title", "Title:"
    if re.match(rf"^(?:\d+\s*[\.\)]\s*)?{re.escape(t)}$", first):
        return "\n".join(lines[1:]).lstrip("\n")
    return text


def _normalize_subheaders(md: str) -> str:
    """
    Normalize noisy internal headings to compact bold labels INSIDE a section body.

    Transforms ANY standalone heading-style line into "**Title:**":
      - '### Title' / '#### Title' / etc.
      - '1. Title' / '1) Title'
      - '📌 **Title**' / '- **Title**'
      - '**Title**' on its own line
      - Optional trailing colon handled; emojis/bullets stripped.
    Does NOT touch list items that have content after the heading word.
    """

    # 1) Hash headings -> bold label
    def h_repl(m):
        title = m.group(1).strip()
        title = re.sub(rf"^{_EMOJI_BULLETS}\s*", "", title).strip()
        title = re.sub(r"[*_`#]+", "", title).strip()
        if not title.endswith(":"):
            title += ":"
        return f"**{title}**"

    md = re.sub(r"^\s*#{2,6}\s+([^\n#].*?)\s*$", h_repl, md, flags=re.MULTILINE)

    # 2) Standalone numbered headings (no trailing content) -> bold label
    md = re.sub(
        r"^\s*\d+\s*[\.\)]\s*([A-Za-z][^\n:]{0,120}?)\s*:?\s*$",
        lambda m: f"**{m.group(1).strip() if m.group(1).strip().endswith(':') else m.group(1).strip() + ':'}**",
        md,
        flags=re.MULTILINE,
    )

    # 3) Emoji/bullet + **Heading** (standalone) -> bold label
    md = re.sub(
        rf"^\s*(?:{_EMOJI_BULLETS}\s*)?\*\*\s*([^\*\n].*?)\s*\*\*\s*:?\s*$",
        lambda m: f"**{m.group(1).strip().rstrip(':') + ':'}**",
        md,
        flags=re.MULTILINE,
    )

    # 4) Plain '**Heading**' line -> bold label
    md = re.sub(
        r"^\s*\*\*\s*([^\*\n].*?)\s*\*\*\s*$",
        lambda m: f"**{m.group(1).strip().rstrip(':') + ':'}**",
        md,
        flags=re.MULTILINE,
    )

    # 5) Remove emoji/bullet prefixes that might still precede bold labels
    md = re.sub(rf"^\s*{_EMOJI_BULLETS}\s*(\*\*[^\n]+\*\*)\s*$", r"\1", md, flags=re.MULTILINE)

    # 6) Collapse extra blank lines
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


# =========================
# Section parsing (titles + icons)
# =========================
SectionStyle = Literal["markdown", "info", "warning", "success"]

def _detect_section(raw: str) -> tuple[str, str, str, SectionStyle]:
    """
    Given a section blob, return (icon, title, content, style).
    More aggressive: detects headings whether bold, plain, numbered, or hash-style.
    Strips the matched heading line from the content and also removes a duplicate
    first line like "1. General Information:" if the LLM echoed it again.
    """
    text = raw.strip()
    lower = text.lower()

    # Patterns that match a heading at the START of the blob (one line only)
    base = r"(overview|general information|care instructions|toxicity|propagation|common issues|problems|interesting facts)"
    heading_line_patterns = [
        rf"^\s*\*\*\s*(?:\d+\s*[\.\)]\s*)?{base}\s*:?\s*\*\*\s*$",          # **Title**
        rf"^\s*(?:\d+\s*[\.\)]\s*)?\s*{base}\s*:?\s*$",                      # Title or 1. Title
        rf"^\s*#{2,6}\s+{base}\s*$",                                        # ## Title
    ]

    icon_map = {
        "overview": ("📌", "markdown"),
        "general information": ("📝", "markdown"),
        "care instructions": ("🌱", "markdown"),
        "toxicity": ("⚠️", "warning"),
        "propagation": ("🌿", "markdown"),
        "common issues": ("🐛", "markdown"),
        "problems": ("🐛", "markdown"),
        "interesting facts": ("💡", "info"),
    }

    # Try to detect a leading heading line and strip it
    for pat in heading_line_patterns:
        m = re.match(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            title_key = m.group(1).lower()
            icon, style = icon_map.get(title_key, ("📌", "markdown"))
            content = text[m.end():].lstrip("\n")

            # If toxicity says non-toxic, flip to success
            if title_key == "toxicity" and (
                ("not toxic" in lower) or ("non-toxic" in lower) or ("non toxic" in lower)
            ):
                style = "success"

            # Remove a duplicated first line like "1. General Information:" or "General Information:"
            content = re.sub(
                rf"^\s*(?:\d+\s*[\.\)]\s*)?{re.escape(title_key)}\s*:?\s*$",
                "",
                content,
                count=1,
                flags=re.IGNORECASE | re.MULTILINE,
            ).lstrip("\n")

            return icon, title_key.title(), content, style

    # Fallback: keyword presence anywhere
    for key, (icon, style) in icon_map.items():
        if key in lower:
            content = text
            if key == "toxicity" and (
                ("not toxic" in lower) or ("non-toxic" in lower) or ("non toxic" in lower)
            ):
                style = "success"
            # Also strip a leading line if present
            content = re.sub(
                rf"^\s*(?:\d+\s*[\.\)]\s*)?{re.escape(key)}\s*:?\s*$",
                "",
                content,
                count=1,
                flags=re.IGNORECASE | re.MULTILINE,
            ).lstrip("\n")
            return icon, key.title(), content, style

    # Ultimate fallback: derive from first line
    first_line = text.splitlines()[0] if text else "Details"
    title = first_line.split(":")[0].strip()
    if len(title) > 60:
        title = " ".join(title.split()[:8])
    content = "\n".join(text.splitlines()[1:]).lstrip("\n") if "\n" in text else ""
    return "📌", (title or "Details"), content or text, "markdown"



# =========================
# Main renderer
# =========================
def render_plant_analysis_display(plant_name: str, analysis: str, mute_audio: bool = True):
    """
    Render plant analysis with:
      - Header bar
      - Left: image + quick facts (+ optional audio)
      - Right: clean sections with icon + title; duplicate headings removed
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
            # Image with attribution
            img = get_plant_image_info(plant_name)
            cap = f"🌿 {plant_name}"
            if img.get("page_url"):
                cap += f" • [{img['caption']}]({img['page_url']})"
            else:
                cap += f" • {img['caption']}"
            st.image(img["url"], caption=cap, use_container_width=True)

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
            chunks = re.split(r"\n{2,}", analysis.strip())

            # If first chunk looks like an overall report title/intro, render as "Overview"
            if chunks and (chunks[0].lstrip().startswith("#") or "report" in chunks[0].lower()):
                overview = _normalize_subheaders(_strip_leading_section_line(chunks[0], "Overview"))
                st.markdown('<div class="section-hdr">📌 Overview</div>', unsafe_allow_html=True)
                st.markdown(overview)
                chunks = chunks[1:]

            # Render remaining chunks as sections
            for section in chunks:
                if not section.strip():
                    continue
                icon, title, content, style = _detect_section(section)
                st.markdown(f'<div class="section-hdr">{icon} {title}</div>', unsafe_allow_html=True)
                body = _normalize_subheaders(content)
                if style == "warning":
                    st.warning(body)
                elif style == "success":
                    st.success(body)
                elif style == "info":
                    st.info(body)
                else:
                    st.markdown(body)


# =========================
# Public helpers
# =========================
def render_custom_css():
    load_custom_css()


def render_legal_footer():
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
            <p>Made with ❤️ by Maniwar • Version 2.10.0</p>
            <p style="opacity: 0.8; font-size: 0.9rem;">© 2024 • Powered by OpenAI & Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Backwards compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)
