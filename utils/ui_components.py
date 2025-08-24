"""
UI Components Module
Verbatim LLM rendering + animations (leaf, sheen, typewriter), reliable images
Author: Maniwar
Version: 6.0.0 - Reimagined beautiful particle effects
"""

from __future__ import annotations

import html as _html
import re
from io import BytesIO
from typing import Dict, Optional
from urllib.parse import quote
import hashlib
import random

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
# Reimagined Beautiful Particle System
# =========================================================
def render_particles(
    enabled: bool = True,
    height: int = 150,
    preset: str = "garden",  # New presets: garden, fireflies, pollen, rain, butterflies, bokeh
    intensity: float = 1.0,
    interactive: bool = True,
) -> None:
    """
    Beautifully reimagined particle effects with nature themes.
    
    Presets:
    - garden: Multi-layer garden scene with leaves, petals, and light particles
    - fireflies: Glowing fireflies with realistic movement
    - pollen: Floating pollen with wind effects
    - rain: Gentle rain with splash effects
    - butterflies: Animated butterflies
    - bokeh: Beautiful bokeh light effects
    """
    if not enabled:
        return

    from streamlit.components.v1 import html as _html_iframe
    import json
    
    # Generate unique ID to prevent conflicts
    container_id = f"particles_{random.randint(1000, 9999)}"
    
    # Validate preset
    valid_presets = {"garden", "fireflies", "pollen", "rain", "butterflies", "bokeh"}
    preset = preset.lower() if preset in valid_presets else "garden"
    intensity = max(0.3, min(2.0, float(intensity)))
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                margin: 0; 
                padding: 0; 
                overflow: hidden; 
                background: transparent;
            }}
            #canvas {{
                display: block;
                width: 100%;
                height: 100vh;
                cursor: crosshair;
            }}
        </style>
    </head>
    <body>
        <canvas id="canvas"></canvas>
        <script>
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            let width = canvas.width = window.innerWidth;
            let height = canvas.height = window.innerHeight;
            let mouseX = width / 2;
            let mouseY = height / 2;
            let particles = [];
            let frame = 0;
            
            const PRESET = "{preset}";
            const INTENSITY = {intensity};
            const INTERACTIVE = {str(interactive).lower()};
            
            // Handle resize
            window.addEventListener('resize', () => {{
                width = canvas.width = window.innerWidth;
                height = canvas.height = window.innerHeight;
            }});
            
            // Mouse tracking
            if (INTERACTIVE) {{
                canvas.addEventListener('mousemove', (e) => {{
                    mouseX = e.clientX;
                    mouseY = e.clientY;
                }});
            }}
            
            // Utility functions
            const random = (min, max) => Math.random() * (max - min) + min;
            const distance = (x1, y1, x2, y2) => Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
            
            // Particle class
            class Particle {{
                constructor(config) {{
                    Object.assign(this, config);
                    this.reset();
                }}
                
                reset() {{
                    this.x = random(0, width);
                    this.y = random(-100, height);
                    this.size = this.baseSize * random(0.5, 1.5);
                    this.speedX = random(-0.5, 0.5) * INTENSITY;
                    this.speedY = random(0.2, 1) * INTENSITY;
                    this.opacity = 0;
                    this.targetOpacity = random(0.3, 1);
                    this.rotation = random(0, Math.PI * 2);
                    this.rotationSpeed = random(-0.02, 0.02);
                    this.life = 0;
                    this.maxLife = random(200, 400);
                    this.offsetX = random(-50, 50);
                    this.offsetY = random(-50, 50);
                }}
                
                update() {{
                    // Fade in/out
                    if (this.life < 20) {{
                        this.opacity = (this.life / 20) * this.targetOpacity;
                    }} else if (this.life > this.maxLife - 20) {{
                        this.opacity = ((this.maxLife - this.life) / 20) * this.targetOpacity;
                    }} else {{
                        this.opacity = this.targetOpacity;
                    }}
                    
                    // Movement
                    this.x += this.speedX;
                    this.y += this.speedY;
                    this.rotation += this.rotationSpeed;
                    this.life++;
                    
                    // Reset if needed
                    if (this.life > this.maxLife || this.y > height + 100) {{
                        this.reset();
                    }}
                    
                    // Mouse interaction
                    if (INTERACTIVE && this.interactive !== false) {{
                        const dist = distance(this.x, this.y, mouseX, mouseY);
                        if (dist < 100) {{
                            const angle = Math.atan2(this.y - mouseY, this.x - mouseX);
                            const force = (100 - dist) / 100 * 2;
                            this.x += Math.cos(angle) * force;
                            this.y += Math.sin(angle) * force;
                        }}
                    }}
                }}
                
                draw() {{
                    ctx.save();
                    ctx.globalAlpha = this.opacity;
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation);
                    
                    if (this.type === 'leaf') {{
                        // Draw leaf shape
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.ellipse(0, 0, this.size, this.size * 0.6, 0, 0, Math.PI * 2);
                        ctx.fill();
                    }} else if (this.type === 'petal') {{
                        // Draw petal shape
                        const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size);
                        gradient.addColorStop(0, this.color);
                        gradient.addColorStop(1, this.color2 || this.color);
                        ctx.fillStyle = gradient;
                        ctx.beginPath();
                        ctx.ellipse(0, 0, this.size * 0.8, this.size * 1.2, 0, 0, Math.PI * 2);
                        ctx.fill();
                    }} else if (this.type === 'firefly') {{
                        // Glowing firefly
                        const pulse = Math.sin(frame * 0.05 + this.offsetX) * 0.3 + 0.7;
                        ctx.shadowBlur = this.size * 3 * pulse;
                        ctx.shadowColor = this.color;
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.arc(0, 0, this.size * pulse, 0, Math.PI * 2);
                        ctx.fill();
                    }} else if (this.type === 'rain') {{
                        // Rain drop
                        ctx.strokeStyle = this.color;
                        ctx.lineWidth = this.size;
                        ctx.lineCap = 'round';
                        ctx.beginPath();
                        ctx.moveTo(0, 0);
                        ctx.lineTo(0, this.size * 10);
                        ctx.stroke();
                    }} else if (this.type === 'butterfly') {{
                        // Animated butterfly
                        const wing = Math.sin(frame * 0.1 + this.offsetX) * 0.5 + 0.5;
                        ctx.fillStyle = this.color;
                        // Left wing
                        ctx.beginPath();
                        ctx.ellipse(-this.size * wing, 0, this.size, this.size * 0.7, -0.3, 0, Math.PI * 2);
                        ctx.fill();
                        // Right wing
                        ctx.beginPath();
                        ctx.ellipse(this.size * wing, 0, this.size, this.size * 0.7, 0.3, 0, Math.PI * 2);
                        ctx.fill();
                        // Body
                        ctx.fillStyle = '#4a4a4a';
                        ctx.fillRect(-2, -this.size * 0.5, 4, this.size);
                    }} else if (this.type === 'bokeh') {{
                        // Bokeh light effect
                        const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size);
                        gradient.addColorStop(0, this.color);
                        gradient.addColorStop(0.4, this.color + '88');
                        gradient.addColorStop(1, 'transparent');
                        ctx.fillStyle = gradient;
                        ctx.beginPath();
                        ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                        ctx.fill();
                    }} else {{
                        // Default circle
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                    
                    ctx.restore();
                }}
            }}
            
            // Initialize particles based on preset
            function initParticles() {{
                particles = [];
                
                if (PRESET === 'garden') {{
                    // Multi-layer garden scene
                    // Background bokeh lights
                    for (let i = 0; i < 15 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'bokeh',
                            baseSize: random(20, 40),
                            color: random(0, 1) > 0.5 ? 'rgba(255, 223, 186, 0.3)' : 'rgba(186, 255, 201, 0.3)',
                            speedY: 0.1,
                            interactive: false
                        }}));
                    }}
                    // Falling leaves
                    for (let i = 0; i < 8 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'leaf',
                            baseSize: random(8, 15),
                            color: ['#8ee59b', '#6ee7b7', '#a3e635', '#86efac'][Math.floor(random(0, 4))],
                            speedY: 0.8
                        }}));
                    }}
                    // Floating petals
                    for (let i = 0; i < 12 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'petal',
                            baseSize: random(6, 12),
                            color: 'rgba(255, 182, 193, 0.8)',
                            color2: 'rgba(255, 105, 180, 0.6)',
                            speedY: 0.5
                        }}));
                    }}
                }} else if (PRESET === 'fireflies') {{
                    // Magical fireflies
                    for (let i = 0; i < 25 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'firefly',
                            baseSize: random(2, 4),
                            color: ['#fff59d', '#ffeb3b', '#fffde7'][Math.floor(random(0, 3))],
                            speedX: random(-1, 1),
                            speedY: random(-0.5, 0.5)
                        }}));
                    }}
                }} else if (PRESET === 'pollen') {{
                    // Floating pollen with wind
                    for (let i = 0; i < 40 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'circle',
                            baseSize: random(1, 3),
                            color: 'rgba(255, 235, 59, 0.6)',
                            speedX: Math.sin(frame * 0.01) * 2,
                            speedY: 0.3
                        }}));
                    }}
                }} else if (PRESET === 'rain') {{
                    // Gentle rain
                    for (let i = 0; i < 50 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'rain',
                            baseSize: random(0.5, 1.5),
                            color: 'rgba(174, 213, 255, 0.6)',
                            speedY: random(8, 12),
                            interactive: false
                        }}));
                    }}
                }} else if (PRESET === 'butterflies') {{
                    // Animated butterflies
                    const colors = ['#ff9800', '#e91e63', '#9c27b0', '#2196f3', '#4caf50'];
                    for (let i = 0; i < 10 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'butterfly',
                            baseSize: random(8, 15),
                            color: colors[Math.floor(random(0, colors.length))],
                            speedX: random(-1, 1),
                            speedY: random(-0.5, 0.3)
                        }}));
                    }}
                }} else if (PRESET === 'bokeh') {{
                    // Beautiful bokeh lights
                    const colors = [
                        'rgba(255, 193, 7, 0.4)',
                        'rgba(76, 175, 80, 0.4)',
                        'rgba(3, 169, 244, 0.4)',
                        'rgba(233, 30, 99, 0.4)',
                        'rgba(156, 39, 176, 0.4)'
                    ];
                    for (let i = 0; i < 20 * INTENSITY; i++) {{
                        particles.push(new Particle({{
                            type: 'bokeh',
                            baseSize: random(10, 50),
                            color: colors[Math.floor(random(0, colors.length))],
                            speedX: random(-0.3, 0.3),
                            speedY: random(-0.3, 0.3),
                            interactive: true
                        }}));
                    }}
                }}
            }}
            
            // Animation loop
            function animate() {{
                // Create trail effect for some presets
                if (PRESET === 'fireflies' || PRESET === 'bokeh') {{
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                    ctx.fillRect(0, 0, width, height);
                }} else {{
                    ctx.clearRect(0, 0, width, height);
                }}
                
                // Update and draw particles
                particles.forEach(particle => {{
                    particle.update();
                    particle.draw();
                }});
                
                // Add wind effect for some presets
                if (PRESET === 'pollen' || PRESET === 'garden') {{
                    particles.forEach(particle => {{
                        particle.speedX = Math.sin(frame * 0.01 + particle.offsetX * 0.01) * 0.5 * INTENSITY;
                    }});
                }}
                
                frame++;
                requestAnimationFrame(animate);
            }}
            
            // Start animation
            initParticles();
            animate();
            
            // Reinitialize on preset change (for development)
            window.addEventListener('message', (e) => {{
                if (e.data && e.data.type === 'reinit') {{
                    initParticles();
                }}
            }});
        </script>
    </body>
    </html>
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
    particle_preset: str = "garden",  # New parameter for particle preset
    floating_leaf: bool = True,
    typewriter_subtitle: bool = True,
    allow_model_html: bool = True,
    show_header: bool = False,
    uploaded_image_bytes: Optional[bytes] = None,
) -> None:
    """
    Left: image + quick facts (+ optional audio).
    Right: show LLM output exactly as provided.
    
    Args:
        uploaded_image_bytes: If provided, use this image instead of searching for one
        particle_preset: Choose from 'garden', 'fireflies', 'pollen', 'rain', 'butterflies', 'bokeh'
    """
    # Render beautiful particles
    render_particles(
        enabled=particles, 
        preset=particle_preset,
        intensity=1.0,
        interactive=True
    )

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
          <div>🌿 Plant Facts Explorer • Version 6.0.0</div>
          <div style="opacity:.8;font-size:.9rem;">© 2024 • Powered by OpenAI & Streamlit</div>
        </div>
        """
    )


# Backward compatibility
def get_plant_image(plant_name: str) -> str:
    return get_plant_image_url(plant_name)