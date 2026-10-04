#!/usr/bin/env python3
"""
Vintage Cinema Ticket Generator & Slicer for GitHub Profile READMEs
Inspired by "A Rainy Day in New York (2019)" vintage ticket stub.

Generates:
1. Full monolithic SVGs (Original & Profile editions)
2. High-framerate animated rain GIFs with transparent outer background
3. 5 zero-gap modular slices engineered for GitHub READMEs with distinct hyperlinks
4. Interactive preview HTML & GitHub Actions workflow
"""

import os
import sys
import argparse
import subprocess
import numpy as np
from PIL import Image, ImageDraw
import cairo
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SLICES_DIR = os.path.join(ASSETS_DIR, "slices")
BRAIN_DIR = "/home/gabrielgama/.gemini/antigravity/brain/18274c70-147f-4d8e-8e07-94567acbcf60"

# Dimensions
WIDTH = 394
HEIGHT = 705

# Slice boundaries
# Slice 1: Artwork & Top Perforation (0 to 365, height 365)
# Slice 2: Header & Title (365 to 415, height 50)
# Slice 3: Social & Developer Info (415 to 478, height 63)
# Slice 4: Stats Grid & Side Admission Notches (478 to 572, height 94)
# Slice 5: Handwritten Note & Bottom Perforation (572 to 705, height 133)
SLICE_BOUNDS = [
    (1, 0, 365),
    (2, 365, 50),
    (3, 415, 63),
    (4, 478, 94),
    (5, 572, 133),
]

def load_path_file(filename):
    path = os.path.join(BRAIN_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_arrow_svg(x, y, size=11):
    return f"""<g transform="translate({x}, {y})">
      <line x1="0" y1="{size}" x2="{size}" y2="0" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="{size*0.4}" y1="0" x2="{size}" y2="0" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="{size}" y1="0" x2="{size}" y2="{size*0.6}" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
    </g>"""

def get_umbrella_svg(x, y, scale=1.0):
    return f"""
    <g transform="translate({x}, {y}) scale({scale}) rotate(15)">
      <path d="M -12 0 C -12 -10 12 -10 12 0 C 8 -2 4 -2 0 -1 C -4 -2 -8 -2 -12 0 Z" fill="#111111" />
      <line x1="0" y1="-8" x2="0" y2="-11" stroke="#111111" stroke-width="1.1" stroke-linecap="round" />
      <line x1="0" y1="-1" x2="0" y2="10" stroke="#111111" stroke-width="1.3" stroke-linecap="round" />
      <path d="M 0 10 C 0 13 -4 13 -4 10" fill="none" stroke="#111111" stroke-width="1.3" stroke-linecap="round" />
    </g>"""

def cairo_text_to_path(lines_spec, width, height):
    """
    lines_spec: list of tuples: (x, y, text, font_family, font_size, is_bold)
    returns SVG path string containing all text as vector curves.
    """
    temp_svg = os.path.join(BRAIN_DIR, "_temp_cairo.svg")
    surf = cairo.SVGSurface(temp_svg, width, height)
    ctx = cairo.Context(surf)
    
    for item in lines_spec:
        x, y, text, font_family, font_size, is_bold = item
        weight = cairo.FONT_WEIGHT_BOLD if is_bold else cairo.FONT_WEIGHT_NORMAL
        ctx.select_font_face(font_family, cairo.FONT_SLANT_NORMAL, weight)
        ctx.set_font_size(font_size)
        ctx.move_to(x, y)
        ctx.text_path(text)
        
    ctx.set_source_rgb(0.07, 0.07, 0.08)
    ctx.fill()
    surf.finish()
    
    tree = ET.parse(temp_svg)
    root = tree.getroot()
    paths = [p.attrib["d"] for p in root.findall(".//{http://www.w3.org/2000/svg}path")]
    if os.path.exists(temp_svg):
        os.remove(temp_svg)
    return " ".join(paths)

class TicketGenerator:
    def __init__(self):
        self.d_ticket = load_path_file("ticket_perimeter_path.txt")
        self.d_art = load_path_file("art_ink_path.txt")
        self.d_quote = load_path_file("quote_clean_path.txt")
        os.makedirs(ASSETS_DIR, exist_ok=True)
        os.makedirs(SLICES_DIR, exist_ok=True)
        os.makedirs(os.path.join(SLICES_DIR, "original"), exist_ok=True)
        os.makedirs(os.path.join(SLICES_DIR, "profile"), exist_ok=True)

    def render_art_base_png(self):
        """Renders static Slice 1 base SVG to crisp PNG with transparent background."""
        base_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} 365" width="{WIDTH}" height="365">
  <defs>
    <clipPath id="t-clip-1"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <!-- Ticket body (vintage off-white paper) -->
  <path d="{self.d_ticket}" fill="#efeee9" />
  <g clip-path="url(#t-clip-1)">
    <path d="{self.d_art}" fill="#111111" fill-rule="evenodd" />
  </g>
</svg>"""
        base_svg_path = os.path.join(BRAIN_DIR, "slice_1_base.svg")
        with open(base_svg_path, "w", encoding="utf-8") as f:
            f.write(base_svg)
            
        base_png_path = os.path.join(BRAIN_DIR, "slice_1_base.png")
        cmd = [
            "google-chrome",
            "--headless",
            f"--screenshot={base_png_path}",
            f"--window-size={WIDTH},365",
            "--default-background-color=00000000",
            f"file://{base_svg_path}"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return base_png_path

    def generate_animated_rain_gif(self, output_gif_path, full_ticket=False, profile_data=None):
        """
        Synthesizes a 24-frame seamless looping rain animation.
        Raindrops fall diagonally with authentic linocut ink streaks,
        respecting umbrella and character occlusion.
        """
        print(f"Generating animated rain GIF -> {os.path.basename(output_gif_path)}...")
        
        # Determine base render
        if not full_ticket:
            base_png = self.render_art_base_png()
            base_img = Image.open(base_png).convert("RGBA")
            h_canvas = 365
            y_min, y_max = 25, 365
        else:
            full_svg_path = os.path.join(BRAIN_DIR, "_full_ticket_base.svg")
            edition = "profile" if profile_data else "original"
            full_svg_content = self.build_full_svg(edition, profile_data)
            with open(full_svg_path, "w", encoding="utf-8") as f:
                f.write(full_svg_content)
            base_png = os.path.join(BRAIN_DIR, "_full_ticket_base.png")
            cmd = [
                "google-chrome",
                "--headless",
                f"--screenshot={base_png}",
                f"--window-size={WIDTH},{HEIGHT}",
                "--default-background-color=00000000",
                f"file://{full_svg_path}"
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            base_img = Image.open(base_png).convert("RGBA")
            h_canvas = HEIGHT
            y_min, y_max = 25, 365

        num_frames = 24
        fps = 24
        slant = 0.16
        travel_h = y_max - y_min

        np.random.seed(42)
        drops = []

        # Layer 1: Fine background drizzle (35 drops)
        for _ in range(35):
            cycles = np.random.choice([1, 2])
            speed = cycles * travel_h / num_frames
            drops.append({
                "x": np.random.uniform(25, 335),
                "y0": np.random.uniform(0, travel_h),
                "len": np.random.uniform(8, 14),
                "speed": speed,
                "width": 1,
                "color": (25, 25, 28, 140)
            })

        # Layer 2: Main linocut rain streaks (45 drops)
        for _ in range(45):
            cycles = np.random.choice([2, 3])
            speed = cycles * travel_h / num_frames
            drops.append({
                "x": np.random.uniform(25, 335),
                "y0": np.random.uniform(0, travel_h),
                "len": np.random.uniform(14, 22),
                "speed": speed,
                "width": 2,
                "color": (15, 15, 18, 220)
            })

        # Layer 3: Heavy fast drops (12 drops)
        for _ in range(12):
            cycles = np.random.choice([3, 4])
            speed = cycles * travel_h / num_frames
            drops.append({
                "x": np.random.uniform(25, 335),
                "y0": np.random.uniform(0, travel_h),
                "len": np.random.uniform(22, 30),
                "speed": speed,
                "width": 2,
                "color": (10, 10, 12, 255)
            })

        frames_dir = os.path.join(BRAIN_DIR, f"gif_frames_{'full' if full_ticket else 'art'}")
        os.makedirs(frames_dir, exist_ok=True)
        base_alpha = np.array(base_img)[:, :, 3] > 80

        for f in range(num_frames):
            overlay = Image.new("RGBA", (WIDTH, h_canvas), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            for d in drops:
                curr_y = (d["y0"] + f * d["speed"]) % travel_h + y_min
                curr_x = d["x"] + (curr_y - y_min) * slant

                # Umbrella dome occlusion
                dx = (curr_x - 212) / 98.0
                dy = (curr_y - 142) / 52.0
                if dx*dx + dy*dy < 0.95 and curr_y < 162:
                    continue

                # Character body & face occlusion
                if 165 < curr_x < 245 and 160 < curr_y < 340:
                    continue

                x_end = curr_x + d["len"] * slant
                y_end = curr_y + d["len"]
                draw.line([(curr_x, curr_y), (x_end, y_end)], fill=d["color"], width=d["width"])

            # Clip rain to ticket alpha silhouette
            overlay_arr = np.array(overlay)
            overlay_arr[~base_alpha] = 0
            overlay_masked = Image.fromarray(overlay_arr)

            composite = Image.alpha_composite(base_img, overlay_masked)
            composite.save(os.path.join(frames_dir, f"frame_{f:03d}.png"))

        # High-quality ffmpeg palette compilation with alpha preservation
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(frames_dir, "frame_%03d.png"),
            "-filter_complex", "[0:v] split [a][b];[a] palettegen=reserve_transparent=on:transparency_color=00000000 [p];[b][p] paletteuse=alpha_threshold=128",
            output_gif_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  -> Generated {output_gif_path} ({os.path.getsize(output_gif_path):,} bytes)")

    def build_slice_1_svg(self, animated=False):
        """Generates Slice 1 SVG (Artwork & Top Scallop)."""
        rain_smil = ""
        if animated:
            rain_smil = """
    <g opacity="0.85">
      <line x1="45" y1="40" x2="48" y2="60" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="85" y1="70" x2="88" y2="90" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="120" y1="50" x2="123" y2="70" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="280" y1="60" x2="283" y2="80" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="315" y1="90" x2="318" y2="110" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="60" y1="130" x2="63" y2="150" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="295" y1="160" x2="298" y2="180" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="110" y1="210" x2="113" y2="230" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="270" y1="240" x2="273" y2="260" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <animateTransform attributeName="transform" type="translate" from="0 -100" to="16 100" dur="0.8s" repeatCount="indefinite" />
    </g>"""

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} 365" width="{WIDTH}" height="365">
  <defs>
    <clipPath id="t-clip-1"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <path d="{self.d_ticket}" fill="#efeee9" />
  <g clip-path="url(#t-clip-1)">
    <path d="{self.d_art}" fill="#111111" fill-rule="evenodd" />
    {rain_smil}
  </g>
</svg>"""

    def build_slice_2_svg(self, edition="profile", profile_data=None):
        """Slice 2: Title & Badge Header (y: 365..415, height 50)"""
        umbrellas = f"{get_umbrella_svg(270, 392, 0.95)} {get_umbrella_svg(295, 392, 0.95)} {get_umbrella_svg(320, 392, 0.95)}"
        
        if edition == "original":
            text_spec = [
                (32, 21, "纽约的一个雨天(2019)", "Noto Serif CJK SC", 17, True),
                (33, 37, "A Rainy Day in New York", "Courier New", 10.5, True)
            ]
        else:
            title = profile_data.get("title", "GABRIEL GAMA · 2026")
            subtitle = profile_data.get("subtitle", "Front-end Developer • Brazil")
            text_spec = [
                (32, 21, title, "Noto Serif CJK SC", 15.5, True),
                (33, 37, subtitle, "Courier New", 10.5, True)
            ]
            
        text_d = cairo_text_to_path(text_spec, WIDTH, 50)
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 365 {WIDTH} 50" width="{WIDTH}" height="50">
  <defs>
    <clipPath id="t-clip-2"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <path d="{self.d_ticket}" fill="#efeee9" />
  <g clip-path="url(#t-clip-2)">
    <g transform="translate(0, 365)">
      <path d="{text_d}" fill="#111111" />
    </g>
    {umbrellas}
    <line x1="30" y1="413" x2="335" y2="413" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
  </g>
</svg>"""

    def build_slice_3_portfolio_svg(self):
        """Slice 3: Portfólio with authentic organic pen underline (height 44)"""
        p_text = cairo_text_to_path([
            (34, 26, "PORTFÓLIO", "DejaVu Serif", 16.5, True),
            (274, 25, "VISIT", "Courier New", 11, True),
        ], WIDTH, 44)
        arrow = get_arrow_svg(316, 16, 10)
        # Organic double pen stroke (like quick hand marking with ballpoint/fountain pen)
        pen_underline = '''
  <path d="M 32 32.0 C 58 31.2, 92 32.6, 122 31.4 C 135 30.9, 143 31.6, 150 31.0" 
        stroke="#111111" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9" />
  <path d="M 38 33.8 C 65 33.2, 98 34.2, 130 33.0 C 139 32.6, 144 33.0, 148 32.4" 
        stroke="#111111" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.75" />
'''
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} 44" width="{WIDTH}" height="44">
  <rect x="19" y="0" width="326" height="44" fill="#efeee9" />
  {pen_underline}
  <path d="{p_text}" fill="#111111" />
  {arrow}
  <line x1="30" y1="43" x2="335" y2="43" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
</svg>"""

    def build_slice_4_linkedin_svg(self):
        """Slice 4: LinkedIn (height 44) - Clean, matching portfolio without dashed stamp box"""
        l_text = cairo_text_to_path([
            (34, 27, "LINKEDIN", "DejaVu Serif", 16.5, True),
            (264, 26, "CONNECT", "Courier New", 11, True),
        ], WIDTH, 44)
        arrow = get_arrow_svg(316, 17, 10)
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} 44" width="{WIDTH}" height="44">
  <rect x="19" y="0" width="326" height="44" fill="#efeee9" />
  <path d="{l_text}" fill="#111111" />
  {arrow}
  <line x1="30" y1="43" x2="335" y2="43" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
</svg>"""

    def build_slice_5_stats_svg(self, edition="profile", profile_data=None):
        """Slice 5: Stats Grid & Circular Admission Notches (height 108, y: 464..572)"""
        if profile_data is None:
            profile_data = {}
        c_val = profile_data.get("commits", "+54 / wk")
        s_val = profile_data.get("streak", "28 days")
        r_val = profile_data.get("rank", "Top 5%")
        l_val = profile_data.get("location", "Salvador, BR")
        d_val = profile_data.get("date", "03/Oct/2026")

        text_spec = [
            (34, 38, "COMMITS", "Fira Sans Condensed", 10.5, True),
            (142, 38, "STREAK", "Fira Sans Condensed", 10.5, True),
            (248, 38, "RANK", "Fira Sans Condensed", 10.5, True),
            (34, 55, c_val, "Fira Mono", 13.5, True),
            (142, 55, s_val, "Fira Mono", 13.5, True),
            (248, 55, r_val, "Fira Mono", 13.5, True),
            (34, 79, "LOCATION", "Fira Sans Condensed", 10.5, True),
            (180, 79, "UPDATED", "Fira Sans Condensed", 10.5, True),
            (34, 96, l_val, "Fira Mono", 13.5, True),
            (180, 96, d_val, "Fira Mono", 13.5, True),
        ]
        text_d = cairo_text_to_path(text_spec, WIDTH, 108)
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 464 {WIDTH} 108" width="{WIDTH}" height="108">
  <defs>
    <clipPath id="t-clip-5"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <path d="{self.d_ticket}" fill="#efeee9" />
  <g clip-path="url(#t-clip-5)">
    <g transform="translate(0, 464)">
      <path d="{text_d}" fill="#111111" />
    </g>
    <!-- Column dividers in row 1 -->
    <line x1="130" y1="496" x2="130" y2="522" stroke="#111111" stroke-width="1.1" stroke-dasharray="1 3" stroke-linecap="round" />
    <line x1="236" y1="496" x2="236" y2="522" stroke="#111111" stroke-width="1.1" stroke-dasharray="1 3" stroke-linecap="round" />
    <!-- Row divider -->
    <line x1="34" y1="531" x2="330" y2="531" stroke="#111111" stroke-width="1.0" stroke-dasharray="2 3" stroke-linecap="round" opacity="0.6" />
    <!-- Column divider in row 2 -->
    <line x1="168" y1="537" x2="168" y2="563" stroke="#111111" stroke-width="1.1" stroke-dasharray="1 3" stroke-linecap="round" />
    <!-- Bottom line -->
    <line x1="30" y1="571" x2="335" y2="571" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
  </g>
</svg>"""

    def build_slice_6_note_svg(self, edition="profile", profile_data=None):
        """Slice 6: Handwritten Note & Bottom Scalloped Perforation (y: 572..705, height 133)"""
        quote_content = f'<path d="{self.d_quote}" fill="#111111" fill-rule="evenodd" />'
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 572 {WIDTH} 133" width="{WIDTH}" height="133">
  <defs>
    <clipPath id="t-clip-6"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <path d="{self.d_ticket}" fill="#efeee9" />
  <g clip-path="url(#t-clip-6)">
    {quote_content}
  </g>
</svg>"""

    def build_full_svg(self, edition="profile", profile_data=None, animated=False):
        """Builds full monolithic master SVG ticket."""
        umbrellas = f"{get_umbrella_svg(270, 392, 0.95)} {get_umbrella_svg(295, 392, 0.95)} {get_umbrella_svg(320, 392, 0.95)}"
        
        if edition == "original":
            t2 = cairo_text_to_path([
                (32, 21, "纽约的一个雨天(2019)", "Noto Serif CJK SC", 17, True),
                (33, 37, "A Rainy Day in New York", "Courier New", 10.5, True)
            ], WIDTH, 50)
            t3 = cairo_text_to_path([
                (32, 17, "〔美国〕伍迪·艾伦 Woody Allen", "Noto Serif CJK SC", 11.5, True),
                (33, 31, "Comedy/Romance", "Courier New", 10, True),
                (32, 45, "26/Jul/2019(波兰) / 2022-02-25(中国大陆) / 92分钟", "Noto Serif CJK SC", 9, False)
            ], WIDTH, 63)
            t4 = cairo_text_to_path([
                (33, 22, "HALL :", "Courier New", 11, True),
                (145, 22, "SEAT :", "Courier New", 11, True),
                (255, 22, "PRICE :", "Courier New", 11, True),
                (33, 39, "06", "Courier New", 12, True),
                (145, 39, "06-08", "Courier New", 12, True),
                (255, 39, "39.9", "Courier New", 12, True),
                (33, 62, "DATE :", "Courier New", 11, True),
                (145, 62, "TIME :", "Courier New", 11, True),
                (33, 79, "20/Jul/2025", "Courier New", 12, True),
                (145, 79, "20:00 - 21:32", "Courier New", 12, True),
            ], WIDTH, 94)
        else:
            title = profile_data.get("title", "GABRIEL GAMA · 2026")
            subtitle = profile_data.get("subtitle", "Front-end Developer • Brazil")
            role = profile_data.get("role", "〔BR〕Gabriel Gama · Front-end Developer")
            stack = profile_data.get("stack", "React · TypeScript · UI Architecture · SVGs")
            links = profile_data.get("links", "LinkedIn: /in/gabriel-gama · Portfolio: gabrielbaiano.vercel.app")
            c_val = profile_data.get("commits", "+54 / wk")
            s_val = profile_data.get("streak", "28 days")
            r_val = profile_data.get("rank", "Top 5%")
            l_val = profile_data.get("location", "Salvador, BR")
            d_val = profile_data.get("date", "03/Oct/2026")
            
            t2 = cairo_text_to_path([
                (32, 21, title, "Noto Serif CJK SC", 15.5, True),
                (33, 37, subtitle, "Courier New", 10.5, True)
            ], WIDTH, 50)
            t3 = cairo_text_to_path([
                (32, 17, role, "Noto Serif CJK SC", 11, True),
                (33, 31, stack, "Courier New", 9.5, True),
                (32, 45, links, "Noto Serif CJK SC", 8.5, False)
            ], WIDTH, 63)
            t4 = cairo_text_to_path([
                (34, 20, "COMMITS", "Fira Sans Condensed", 10.5, True),
                (142, 20, "STREAK", "Fira Sans Condensed", 10.5, True),
                (248, 20, "RANK", "Fira Sans Condensed", 10.5, True),
                (34, 37, c_val, "Fira Mono", 13.5, True),
                (142, 37, s_val, "Fira Mono", 13.5, True),
                (248, 37, r_val, "Fira Mono", 13.5, True),
                (34, 61, "LOCATION", "Fira Sans Condensed", 10.5, True),
                (180, 61, "UPDATED", "Fira Sans Condensed", 10.5, True),
                (34, 78, l_val, "Fira Mono", 13.5, True),
                (180, 78, d_val, "Fira Mono", 13.5, True),
            ], WIDTH, 94)

        rain_layer = ""
        if animated:
            rain_layer = """
    <g opacity="0.85">
      <line x1="45" y1="40" x2="48" y2="60" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="85" y1="70" x2="88" y2="90" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="120" y1="50" x2="123" y2="70" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="280" y1="60" x2="283" y2="80" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="315" y1="90" x2="318" y2="110" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="60" y1="130" x2="63" y2="150" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="295" y1="160" x2="298" y2="180" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="110" y1="210" x2="113" y2="230" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <line x1="270" y1="240" x2="273" y2="260" stroke="#111111" stroke-width="1.8" stroke-linecap="round" />
      <animateTransform attributeName="transform" type="translate" from="0 -100" to="16 100" dur="0.8s" repeatCount="indefinite" />
    </g>"""

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <defs>
    <clipPath id="ticket-clip"><path d="{self.d_ticket}" /></clipPath>
  </defs>
  <path d="{self.d_ticket}" fill="#efeee9" stroke="#dfded9" stroke-width="0.5" />
  <g clip-path="url(#ticket-clip)">
    <path d="{self.d_art}" fill="#111111" fill-rule="evenodd" />
    {rain_layer}
    <g transform="translate(0, 365)"><path d="{t2}" fill="#111111" /></g>
    {umbrellas}
    <line x1="30" y1="413" x2="335" y2="413" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
    <g transform="translate(0, 415)"><path d="{t3}" fill="#111111" /></g>
    <line x1="30" y1="478" x2="335" y2="478" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
    <g transform="translate(0, 478)"><path d="{t4}" fill="#111111" /></g>
    <line x1="30" y1="571" x2="335" y2="571" stroke="#111111" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round" />
    <path d="{self.d_quote}" fill="#111111" fill-rule="evenodd" />
  </g>
</svg>"""

    def generate_all(self, profile_data=None):
        if profile_data is None:
            profile_data = {
                "title": "GABRIEL GAMA · 2026",
                "subtitle": "Front-end Developer • Brazil",
                "role": "〔BR〕Gabriel Gama · Front-end Developer",
                "stack": "React · TypeScript · UI Architecture · SVGs",
                "links": "LinkedIn: /in/gabriel-gama · Portfolio: gabrielbaiano.vercel.app",
                "commits": "+54 / wk",
                "streak": "28 days",
                "rank": "Top 5%",
                "location": "Salvador, BR",
                "date": "03/Oct/2026"
            }

        print("=== Generating Master SVGs ===")
        orig_svg = self.build_full_svg("original")
        with open(os.path.join(ASSETS_DIR, "ticket_original.svg"), "w", encoding="utf-8") as f:
            f.write(orig_svg)
        print("Generated ticket_original.svg")

        prof_svg = self.build_full_svg("profile", profile_data)
        with open(os.path.join(ASSETS_DIR, "ticket_profile.svg"), "w", encoding="utf-8") as f:
            f.write(prof_svg)
        print("Generated ticket_profile.svg")

        anim_svg = self.build_full_svg("profile", profile_data, animated=True)
        with open(os.path.join(ASSETS_DIR, "ticket_animated.svg"), "w", encoding="utf-8") as f:
            f.write(anim_svg)
        print("Generated ticket_animated.svg")

        print("=== Generating Slices ===")
        # Slices for profile
        with open(os.path.join(SLICES_DIR, "slice_02_header.svg"), "w", encoding="utf-8") as f:
            f.write(self.build_slice_2_svg("profile", profile_data))
        with open(os.path.join(SLICES_DIR, "slice_03_portfolio.svg"), "w", encoding="utf-8") as f:
            f.write(self.build_slice_3_portfolio_svg())
        with open(os.path.join(SLICES_DIR, "slice_04_linkedin.svg"), "w", encoding="utf-8") as f:
            f.write(self.build_slice_4_linkedin_svg())
        with open(os.path.join(SLICES_DIR, "slice_05_stats.svg"), "w", encoding="utf-8") as f:
            f.write(self.build_slice_5_stats_svg("profile", profile_data))
        with open(os.path.join(SLICES_DIR, "slice_06_note.svg"), "w", encoding="utf-8") as f:
            f.write(self.build_slice_6_note_svg("profile", profile_data))

        # Mirror slices to profile subdirectory
        prof_slices_dir = os.path.join(SLICES_DIR, "profile")
        for s_name in ["slice_02_header.svg", "slice_03_portfolio.svg", "slice_04_linkedin.svg", "slice_05_stats.svg", "slice_06_note.svg"]:
            src = os.path.join(SLICES_DIR, s_name)
            dst = os.path.join(prof_slices_dir, s_name)
            with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8") as f_out:
                f_out.write(f_in.read())

        print("=== Generating Animated GIFs ===")
        slice_1_gif = os.path.join(SLICES_DIR, "slice_01_art.gif")
        if not os.path.exists(slice_1_gif):
            self.generate_animated_rain_gif(slice_1_gif, full_ticket=False)

        full_prof_gif = os.path.join(ASSETS_DIR, "ticket_profile.gif")
        if not os.path.exists(full_prof_gif):
            self.generate_animated_rain_gif(full_prof_gif, full_ticket=True, profile_data=profile_data)

        print("=== Generating Profile Markdown Snippet ===")
        self.generate_profile_snippet()

        print("=== Generating Interactive Preview HTML ===")
        self.generate_preview_html()
        print("All assets generated successfully!")

    def generate_profile_snippet(self):
        snippet = """<!-- VINTAGE CINEMA TICKET PROFILE COMPONENT -->
<!-- Engineered with zero-gap p + align=top slicing for GitHub Markdown -->
<p align="center">
  <a href="https://gabrielbaiano.vercel.app/" title="Portfolio"><img src="ticket-profile/assets/slices/slice_01_art.gif" width="394" align="top" alt="A Rainy Day in New York Illustration" /></a><br><a href="https://gabrielbaiano.vercel.app/" title="Gabriel Gama - Front-end Developer"><img src="ticket-profile/assets/slices/slice_02_header.svg" width="394" align="top" alt="Ticket Header" /></a><br><a href="https://gabrielbaiano.vercel.app/" title="Portfólio"><img src="ticket-profile/assets/slices/slice_03_portfolio.svg" width="394" align="top" alt="Portfólio" /></a><br><a href="https://www.linkedin.com/in/gabriel-gama-6301633b2/" title="Connect on LinkedIn"><img src="ticket-profile/assets/slices/slice_04_linkedin.svg" width="394" align="top" alt="LinkedIn" /></a><br><a href="https://github.com/GabrielBaiano?tab=repositories" title="View GitHub Repositories"><img src="ticket-profile/assets/slices/slice_05_stats.svg" width="394" align="top" alt="Commit Activity & Stats" /></a><br><a href="https://gabrielbaiano.vercel.app/" title="Daily Note"><img src="ticket-profile/assets/slices/slice_06_note.svg" width="394" align="top" alt="Vintage Handwritten Note" /></a>
</p>
"""
        with open(os.path.join(BASE_DIR, "profile_snippet.md"), "w", encoding="utf-8") as f:
            f.write(snippet)

    def generate_preview_html(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vintage Cinema Ticket Profile - Preview</title>
<style>
  body {
    margin: 0;
    padding: 40px 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  .theme-dark {
    background-color: #0d1117;
    color: #e6edf3;
  }
  .theme-light {
    background-color: #ffffff;
    color: #1f2328;
  }
  .container {
    max-width: 900px;
    margin: 0 auto;
    text-align: center;
  }
  .controls {
    margin-bottom: 30px;
    display: flex;
    justify-content: center;
    gap: 12px;
  }
  button {
    background: #238636;
    color: #fff;
    border: none;
    padding: 8px 16px;
    font-size: 14px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
  }
  button.secondary {
    background: #30363d;
  }
  .ticket-wrapper {
    display: inline-block;
    padding: 20px;
  }
  table {
    border-collapse: collapse;
    border-spacing: 0;
    margin: 0 auto;
    padding: 0;
    border: none;
  }
  td {
    padding: 0;
    margin: 0;
    line-height: 0;
    font-size: 0;
    border: none;
  }
  img {
    display: block;
    border: none;
    margin: 0;
    padding: 0;
  }
  .grid-preview {
    display: flex;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
    margin-top: 20px;
  }
  .card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 20px;
  }
  h2 {
    font-size: 18px;
    margin-top: 0;
    margin-bottom: 16px;
  }
</style>
</head>
<body class="theme-dark" id="preview-body">
<div class="container">
  <h1>Vintage Cinema Ticket GitHub Profile</h1>
  <p>Zero-gap sliced architecture with transparent outer background and animated rain</p>
  
  <div class="controls">
    <button onclick="setTheme('dark')">GitHub Dark Theme</button>
    <button class="secondary" onclick="setTheme('light')">GitHub Light Theme</button>
  </div>

  <div class="grid-preview">
    <div class="card">
      <h2>Sliced GitHub README Component (Clickable Links)</h2>
      <div class="ticket-wrapper">
        <p align="center" style="margin: 0; padding: 0;">
          <a href="https://gabrielbaiano.vercel.app/" target="_blank"><img src="assets/slices/slice_01_art.gif" width="394" align="top" /></a><br><a href="https://gabrielbaiano.vercel.app/" target="_blank"><img src="assets/slices/slice_02_header.svg" width="394" align="top" /></a><br><a href="https://gabrielbaiano.vercel.app/" target="_blank"><img src="assets/slices/slice_03_portfolio.svg" width="394" align="top" /></a><br><a href="https://www.linkedin.com/in/gabriel-gama-6301633b2/" target="_blank"><img src="assets/slices/slice_04_linkedin.svg" width="394" align="top" /></a><br><a href="https://github.com/GabrielBaiano" target="_blank"><img src="assets/slices/slice_05_stats.svg" width="394" align="top" /></a><br><a href="https://gabrielbaiano.vercel.app/" target="_blank"><img src="assets/slices/slice_06_note.svg" width="394" align="top" /></a>
        </p>
      </div>
    </div>

    <div class="card">
      <h2>Full Monolithic Animated GIF</h2>
      <div class="ticket-wrapper">
        <img src="assets/ticket_profile.gif" width="394" height="705" />
      </div>
    </div>
  </div>
</div>

<script>
  function setTheme(t) {
    document.getElementById('preview-body').className = t === 'dark' ? 'theme-dark' : 'theme-light';
  }
</script>
</body>
</html>"""
        with open(os.path.join(BASE_DIR, "preview.html"), "w", encoding="utf-8") as f:
            f.write(html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Vintage Cinema Ticket")
    parser.add_argument("--commits", default="+54 / wk", help="Weekly commits count")
    parser.add_argument("--streak", default="28 days", help="Active streak")
    parser.add_argument("--rank", default="Top 5%", help="Rank or badge")
    parser.add_argument("--date", default="03/Oct/2026", help="Ticket date")
    parser.add_argument("--location", default="Salvador, BR", help="Location")
    args = parser.parse_args()

    gen = TicketGenerator()
    data = {
        "title": "GABRIEL GAMA · 2026",
        "subtitle": "Front-end Developer • Brazil",
        "role": "〔BR〕Gabriel Gama · Front-end Developer",
        "stack": "React · TypeScript · UI Architecture · SVGs",
        "links": "LinkedIn: /in/gabriel-gama · Portfolio: gabrielbaiano.vercel.app",
        "commits": args.commits,
        "streak": args.streak,
        "rank": args.rank,
        "location": args.location,
        "date": args.date
    }
    gen.generate_all(data)
