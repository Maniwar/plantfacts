"""
UI Components Module
LLM-tolerant parsing, clean sections, reliable images, subtle animations
Author: Maniwar
Version: 4.2.0
"""

from __future__ import annotations

import html as _html
import re
from io import BytesIO
from typing import Dict, List, Optional, Tuple
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
            --chip-bg: rgba(102,126,234,.12);
            --chip-br: rgba(148,163,184,.35);
            --panel-bg: rgba(2,6,23,.20);
            --panel-br: rgba(148,163,184,.25);
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
          .subtitle { opacity:.95; margin:.45rem 0 0 0; }

          .bar-title {
            background:linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 100%);
            color:#fff; font-weight:700; padding:.8rem 1rem; border-radius:12px;
            display:flex; align-items:center; gap:.6rem; margin-top:.3rem;
          }

          .stImage { border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,.12); }

          /* Section chip */
          .chip {
            display:inline-flex; align-items:center; gap:.5rem; font-weight:700;
            padding:.45rem .7rem; border-radius:999px;
            border:1px solid var(--chip-br);
            background: var(--chip-bg);
            margin:.9rem 0 .35rem 0; font-family:'Space Grotesk',sans-serif;
          }

          /* Key/Value panel */
          .kv-panel {
            border:1px solid var(--panel-br); background:var(--panel-bg);
            border-radius:12px; padding:.55rem .7rem; margin:.35rem 0 .75rem 0;
          }

          /* Respect reduced motion */
          @media (prefers-reduced-motion: reduce) {
            .sheen, .leaf { animation: none !important; }
          }
          @keyframes shimmer { 0%,100%{transform:translateX(0)} 50%{transform:translateX(18px)} }
          @keyframes float   { 0%,100%{transform:translateY(0) rotate(0deg)} 50%{transform:translateY(-10px) rotate(6deg)} }

          /* Minor list spacing */
          .stMarkdown ul { margin:.3rem 0 .6rem 1rem; }
          .stMarkdown p:empty { display:none!important; }
        </style>
        """
    )


def render_header(
    subtitle: str = "Discover the amazing world of plants with AI-powered insights",
    show_leaf: bool = True,
) -> None:
    leaf = '<span class="leaf">🌿</span>' if show_leaf else ""
    st.html(
        f"""
        <div class="header">
          <div class="sheen"></div>
          <div class="title-row">
            {leaf}
            <div class="headline">Plant Facts Explorer</div>
          </div>
          <div class="subtitle">{_html.escape(subtitle)}</div>
        </div>
        """
    )


# =========================================================
# Optional particle background (JS in iframe)
# =========================================================
def render_particles(enabled: bool = False) -> None:
    if not enabled:
        return
    components.html(
        """
        <!doctype html><html><head><meta charset="utf-8"/>
        <style>
          html,body,#tsparticles { margin:0; padding:0; height:100%; width:100%; background:transparent; }
        </style></head><body>
          <div id="tsparticles"></div>
          <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.12.0/tsparticles.bundle.min.js"></script>
          <script>
            (async () => {
              const engine = window.tsParticles;
              await engine.load("tsparticles", {
                background: { color: { value: "transparent" } },
                fpsLimit: 45,
                particles: {
                  number: { value: 34, density: { enable: true, area: 800 } },
                  color: { value: ["#a7f3d0", "#93c5fd", "#c4b5fd"] },
                  opacity: { value: 0.25 },
                  size: { value: { min: 1, max: 3 } },
                  move: { enable: true, speed: 0.8, direction: "none", outModes: { default: "out" } },
                  links: { enable: true, distance: 120, opacity: 0.12, color: "#cbd5e1" },
                },
                detectRetina: true,
                fullScreen: { enable: true, zIndex: 0 }
              });
            })();
          </script>
        </body></html>
        """,
        height=220,
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


def get_plant_image_url(plant_name: str) -> str:
    return get_plant_image_info(plant_name)["url"]


# =========================================================
# Quick facts
# =========================================================
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


# =========================================================
# Robust LLM parsing
# =========================================================
SECTION_KEYS: List[Tuple[str, str]] = [
    ("overview", "📌"),
    ("general information", "📝"),
    ("care instructions", "🌱"),
    ("toxicity", "⚠️"),
    ("propagation", "🌿"),
    ("common issues", "🐛"),
    ("interesting facts", "💡"),
]
_SECTION_TITLES = [k for k, _ in SECTION_KEYS]
_SECTION_ICON = {k: icon for k, icon in SECTION_KEYS}


def _normalize_infix_headings(text: str) -> str:
    """
    LLMs sometimes cram '##' or numbered headings inline.
    Insert a newline BEFORE any '##'/'###'/numbered/emoji+bold heading
    that appears mid-line, so downstream regex can split properly.
    """
    t = text.replace("\r\n", "\n")

    # Newline before '##' / '###' tokens when not already at start of a line
    t = re.sub(r"(?<!\n)\s+(##\s+)", r"\n\1", t)
    t = re.sub(r"(?<!\n)\s+(###\s+)", r"\n\1", t)

    # Newline before patterns like ' 1. Title' or ' 2) Title'
    t = re.sub(r"(?<!\n)\s+(\d+\s*[\.\)]\s+)", r"\n\1", t)

    # Newline before emoji+bold headings like ' 📌 **Common Name**'
    t = re.sub(r"(?<!\n)\s*([📌📝🌱⚠️🌿🐛💡]\s*\*\*)", r"\n\1", t)

    return t



def _split_sections(text: str) -> List[Tuple[str, str, str]]:
    """
    Split the report into (title, icon, body) tuples.
    Accepts headings like '## Title', '**Title**', 'Title:', '1. Title', etc.
    """
    src = _normalize_infix_headings(text).strip()
    if not src:
        return []

    titles = "|".join(map(re.escape, _SECTION_TITLES))
    heading_line = re.compile(
        rf"^\s*(?:\#{{2,6}}\s*|(?:\*\*)?\s*(?:\d+\s*[\.\)]\s*)?)({titles})\s*:?\s*(?:\*\*)?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(heading_line.finditer(src))

    out: List[Tuple[str, str, str]] = []

    # If no headings, treat all as Overview after trimming obvious global title lines
    if not matches:
        cleaned = _strip_global_title(src)
        out.append(("Overview", "📌", cleaned))
        return out

    # Intro before first heading = Overview (minus global title lines)
    if matches[0].start() > 0:
        intro = _strip_global_title(src[: matches[0].start()].strip())
        if intro:
            out.append(("Overview", "📌", intro))

    for i, m in enumerate(matches):
        title_key = m.group(1).lower()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
        chunk = src[m.end() : end].strip()
        icon = _SECTION_ICON.get(title_key, "📌")
        out.append((title_key.title(), icon, chunk))

    return out


def _strip_global_title(text: str) -> str:
    """
    Remove huge leading titles like 'Comprehensive Report on ...' so the
    first section shows neatly.
    """
    t = re.sub(r"^\s*#+\s+.*$", "", text, flags=re.MULTILINE)  # drop H1/H2 lines
    t = re.sub(r"^\s*(Comprehensive|Complete|Detailed)\s+Report.*$", "", t, flags=re.IGNORECASE | re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t


def _extract_blocks(body: str) -> Tuple[List[Tuple[str, str]], List[str], List[str]]:
    """
    From a section body, extract:
      - kv: list[(key, value)] for key/value pairs
      - paras: list[str] paragraphs
      - bullets: list[str] bullet items

    Robust behavior:
      • Handles "Label: Value" on the SAME line
      • Handles label-only lines (e.g., "**Common Name**" or "### Scientific Name" or "Common Name:")
        by taking the NEXT non-empty, non-heading, non-bullet line as the value
      • Keeps original bullets
    """
    # Remove duplicated section-title echoes like "1. General Information:" or "General Information:"
    title_echo = r"^(?:\d+\s*[\.\)]\s*)?(overview|general information|care instructions|toxicity|propagation|common issues|interesting facts)\s*:?\s*$"
    body = re.sub(title_echo, "", body, flags=re.IGNORECASE | re.MULTILINE).strip()

    lines = [ln.rstrip() for ln in body.split("\n")]

    kv: List[Tuple[str, str]] = []
    bullets: List[str] = []
    paras: List[str] = []
    pbuf: List[str] = []

    # Patterns
    pat_bold_kv   = re.compile(r"^\s*\*\*\s*([^*\n]+?)\s*\*\*\s*:?\s*(.+?)\s*$")
    pat_plain_kv  = re.compile(r"^(?!\s*[-*]\s)([A-Z][A-Za-z0-9 \-/]{2,60})\s*:\s*(.+?)\s*$")
    # Label-only (no value on this line) — accepts **Label**, ### Label, or plain Label[:]
    pat_label_only = re.compile(
        r"^\s*(?:\*\*\s*([^*\n]+?)\s*\*\*|#{2,6}\s+([^\n]+?)|([A-Z][A-Za-z0-9 \-/]{2,60}))\s*:?\s*$"
    )
    pat_heading_like_next = re.compile(  # used to decide if a next line is another heading/bullet
        r"^\s*(?:[-*]\s+|#{2,6}\s+|\*\*[^*\n]+?\*\*\s*:?\s*$|[A-Z][A-Za-z0-9 \-/]{2,60}\s*:\s*$)"
    )

    def flush_paragraph():
        nonlocal pbuf, paras
        if any(s.strip() for s in pbuf):
            paras.append(" ".join(s.strip() for s in pbuf if s.strip()))
        pbuf = []

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line = raw.strip()

        # Skip empty lines early
        if not line:
            i += 1
            continue

        # Bullets
        if line.startswith(("- ", "* ")):
            flush_paragraph()
            bullets.append(line[2:].strip())
            i += 1
            continue

        # KV on the same line (bold or plain)
        m = pat_bold_kv.match(line) or pat_plain_kv.match(line)
        if m:
            flush_paragraph()
            key = (m.group(1) or "").strip().rstrip(":")
            val = (m.group(2) or "").strip()
            kv.append((key, val))
            i += 1
            continue

        # Label-only line: take next non-empty, non-heading/bullet line as the value
        m = pat_label_only.match(line)
        if m:
            flush_paragraph()
            key = (m.group(1) or m.group(2) or m.group(3) or "").strip().rstrip(":")
            value = ""
            j = i + 1
            while j < n:
                nxt = lines[j].strip()
                if not nxt:  # skip blank lines between label and value
                    j += 1
                    continue
                # if the next is clearly another heading/bullet/label, stop (no value captured)
                if pat_heading_like_next.match(nxt):
                    break
                value = nxt
                j += 1
                break
            kv.append((key, value))
            i = j if j > i + 1 else i + 1
            continue

        # Otherwise, it's paragraph text
        pbuf.append(line)
        i += 1

    flush_paragraph()
    return kv, paras, bullets


# =========================================================
# Main renderer
# =========================================================
def render_plant_analysis_display(
    plant_name: str,
    analysis: str,
    mute_audio: bool = True,
    particles: bool = False,
    floating_leaf: bool = True,
) -> None:
    """
    Left: image + quick facts (+ optional audio).
    Right: section chips + kv grid + paragraphs + bullets.
    """
    render_particles(enabled=particles)
    render_header(show_leaf=floating_leaf)

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
            i = 0
            for label, value in facts.items():
                with cols[i % 2]:
                    st.metric(label=label, value=value)
                i += 1

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
        sections = _split_sections(analysis) or [("Overview", "📌", _strip_global_title(analysis))]
        for title, icon, body in sections:
            _render_section(title, icon, body)

def _render_section(title: str, icon: str, body: str) -> None:
    """
    Render one section neatly:
      - section chip header
      - key/value grid
      - paragraphs
      - bullet lists
    """
    # Chip header
    st.html(f'<div class="chip">{_html.escape(icon)} {_html.escape(title)}</div>')

    # Extract content blocks
    kv, paras, bullets = _extract_blocks(body)

    # Key/Value grid
    if kv:
        st.html("<div class='kv-panel'></div>")
        for k, v in kv:
            c1, c2 = st.columns([1, 3], gap="small")
            with c1:
                st.markdown(f"**{k}:**")
            with c2:
                st.markdown(v if v else "—")

    # Paragraphs
    for p in paras:
        st.markdown(p)

    # Bullets
    if bullets:
        st.markdown("\n".join(f"- {b}" for b in bullets))

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
          <div>🌿 Plant Facts Explorer • Version 4.2.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)
