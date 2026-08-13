import random
import math
import PIL.Image
import PIL.ImageEnhance
import PIL.ImageOps
import PIL.ImageFilter
import PIL.ImageDraw
import numpy as np

def generate_kotlin_dots(grid_w=300, grid_h=340, is_dark=True):
    img = PIL.Image.new('L', (grid_w, grid_h), 0)
    draw = PIL.ImageDraw.Draw(img)

    top_poly = [(160, 60), (220, 60), (120, 165), (70, 165)]
    bottom_poly = [(125, 175), (220, 270), (165, 270), (70, 175)]
    
    draw.polygon(top_poly, fill=230)
    draw.polygon(bottom_poly, fill=230)

    img_blur = img.filter(PIL.ImageFilter.GaussianBlur(radius=1.5))
    arr = np.array(img_blur, dtype=float)

    for y in range(grid_h):
        for x in range(grid_w):
            old_val = arr[y, x]
            new_val = 255.0 if old_val > 100 else 0.0
            arr[y, x] = new_val
            err = old_val - new_val
            if x + 1 < grid_w:
                arr[y, x + 1] += err * 7 / 16
            if y + 1 < grid_h:
                if x > 0:
                    arr[y + 1, x - 1] += err * 3 / 16
                arr[y + 1, x] += err * 5 / 16
                if x + 1 < grid_w:
                    arr[y + 1, x + 1] += err * 1 / 16

    dots = (arr > 120) if is_dark else (arr <= 120)
    
    runs_by_row = []
    for y in range(grid_h):
        row_runs = []
        x = 0
        while x < grid_w:
            if dots[y, x]:
                x_start = x
                while x < grid_w and dots[y, x]:
                    x += 1
                length = x - x_start
                row_runs.append((x_start, y, length))
            else:
                x += 1
        runs_by_row.extend(row_runs)

    return runs_by_row

def generate_code_brackets_dots(grid_w=300, grid_h=340, is_dark=True):
    img = PIL.Image.new('L', (grid_w, grid_h), 0)
    draw = PIL.ImageDraw.Draw(img)

    # Compact, wider, flattened < / > symbol coordinates
    draw.polygon([(95, 125), (55, 170), (95, 215), (110, 205), (75, 170), (110, 135)], fill=230)
    draw.polygon([(168, 110), (142, 230), (126, 230), (152, 110)], fill=230)
    draw.polygon([(205, 125), (245, 170), (205, 215), (190, 205), (225, 170), (190, 135)], fill=230)

    img_blur = img.filter(PIL.ImageFilter.GaussianBlur(radius=1.5))
    arr = np.array(img_blur, dtype=float)

    for y in range(grid_h):
        for x in range(grid_w):
            old_val = arr[y, x]
            new_val = 255.0 if old_val > 100 else 0.0
            arr[y, x] = new_val
            err = old_val - new_val
            if x + 1 < grid_w:
                arr[y, x + 1] += err * 7 / 16
            if y + 1 < grid_h:
                if x > 0:
                    arr[y + 1, x - 1] += err * 3 / 16
                arr[y + 1, x] += err * 5 / 16
                if x + 1 < grid_w:
                    arr[y + 1, x + 1] += err * 1 / 16

    dots = (arr > 120) if is_dark else (arr <= 120)
    
    runs_by_row = []
    for y in range(grid_h):
        row_runs = []
        x = 0
        while x < grid_w:
            if dots[y, x]:
                x_start = x
                while x < grid_w and dots[y, x]:
                    x += 1
                length = x - x_start
                row_runs.append((x_start, y, length))
            else:
                x += 1
        runs_by_row.extend(row_runs)

    return runs_by_row

def build_arif_style_svg(input_photo='F_Formal.png', output_svg='dark.svg', is_dark=True):
    orig_img = PIL.Image.open(input_photo)
    
    if orig_img.mode == 'RGBA':
        alpha_orig = orig_img.split()[-1]
    else:
        alpha_orig = None

    w, h = orig_img.size
    crop_box = (0, 0, w, h)
    
    img_gray = orig_img.convert('L').crop(crop_box)
    if alpha_orig is not None:
        alpha_img = alpha_orig.crop(crop_box)
    else:
        alpha_img = None

    grid_w, grid_h = 300, 340
    
    img_resized = img_gray.resize((grid_w, grid_h), PIL.Image.Resampling.LANCZOS)
    if alpha_img is not None:
        alpha_resized = alpha_img.resize((grid_w, grid_h), PIL.Image.Resampling.LANCZOS)
        alpha_mask = np.array(alpha_resized) > 50
    else:
        alpha_mask = np.ones((grid_h, grid_w), dtype=bool)

    # 2. Contrast & Sharpening
    img_prep = PIL.ImageOps.autocontrast(img_resized, cutoff=1)
    enhancer = PIL.ImageEnhance.Contrast(img_prep)
    img_prep = enhancer.enhance(1.30)
    img_prep = img_prep.filter(PIL.ImageFilter.UnsharpMask(radius=1.8, percent=135))
    
    arr = np.array(img_prep, dtype=float)

    # 3. Floyd-Steinberg Dithering
    for y in range(grid_h):
        for x in range(grid_w):
            if not alpha_mask[y, x]:
                arr[y, x] = 0.0 if is_dark else 255.0
                continue
            old_val = arr[y, x]
            new_val = 255.0 if old_val > 118 else 0.0
            arr[y, x] = new_val
            err = old_val - new_val
            if x + 1 < grid_w and alpha_mask[y, x + 1]:
                arr[y, x + 1] += err * 7 / 16
            if y + 1 < grid_h:
                if x > 0 and alpha_mask[y + 1, x - 1]:
                    arr[y + 1, x - 1] += err * 3 / 16
                if alpha_mask[y + 1, x]:
                    arr[y + 1, x] += err * 5 / 16
                if x + 1 < grid_w and alpha_mask[y + 1, x + 1]:
                    arr[y + 1, x + 1] += err * 1 / 16

    if is_dark:
        dots = (arr > 120) & alpha_mask
    else:
        dots = (arr <= 120) & alpha_mask

    portrait_runs = []
    for y in range(grid_h):
        x = 0
        while x < grid_w:
            if dots[y, x]:
                x_start = x
                while x < grid_w and dots[y, x]:
                    x += 1
                length = x - x_start
                portrait_runs.append((x_start, y, length))
            else:
                x += 1

    random.seed(2026)
    num_groups = 45

    # --- 1. State 1: Portrait XML (Exact 4.0s stay duration) ---
    portrait_groups = [[] for _ in range(num_groups)]
    for run in portrait_runs:
        g_idx = random.randint(0, num_groups - 1)
        portrait_groups[g_idx].append(run)

    portrait_group_svgs = []
    for idx, g_runs in enumerate(portrait_groups):
        if not g_runs:
            continue
        path_data = "".join([f"M{rx} {ry}h{rlen}v1h-{rlen}z" if rlen > 1 else f"M{rx} {ry}h1v1h-1z" for rx, ry, rlen in g_runs])
        
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(35, 70)
        dx = int(radius * math.cos(angle))
        dy = int(radius * math.sin(angle))

        # 17.4-second total loop for 4.0s stay per state:
        # t=0s..4.0s: Displayed (0 -> 0.230)
        # t=4.0s..5.8s: Scatter transition (0.230 -> 0.333)
        # t=5.8s..15.6s: Hidden (0.333 -> 0.897)
        # t=15.6s..17.4s: Assemble transition (0.897 -> 1.0)
        anim_trans = f'<animateTransform attributeName="transform" type="translate" values="0,0; 0,0; {dx},{dy}; {dx},{dy}; {dx},{dy}; {dx},{dy}; 0,0" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1"/>'
        anim_opac = f'<animate attributeName="opacity" values="1; 1; 0; 0; 0; 0; 1" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite"/>'
        
        g_xml = f'<g>{anim_trans}{anim_opac}<path d="{path_data}"/></g>'
        portrait_group_svgs.append(g_xml)

    portrait_layers_xml = "\n".join(portrait_group_svgs)

    # --- 2. State 2: Kotlin Logo XML ---
    kotlin_runs = generate_kotlin_dots(grid_w, grid_h, is_dark)
    kotlin_groups = [[] for _ in range(num_groups)]
    for run in kotlin_runs:
        g_idx = random.randint(0, num_groups - 1)
        kotlin_groups[g_idx].append(run)

    kotlin_group_svgs = []
    for idx, g_runs in enumerate(kotlin_groups):
        if not g_runs:
            continue
        path_data = "".join([f"M{rx} {ry}h{rlen}v1h-{rlen}z" if rlen > 1 else f"M{rx} {ry}h1v1h-1z" for rx, ry, rlen in g_runs])
        
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(35, 70)
        dx = int(radius * math.cos(angle))
        dy = int(radius * math.sin(angle))

        anim_trans = f'<animateTransform attributeName="transform" type="translate" values="{dx},{dy}; {dx},{dy}; 0,0; 0,0; {dx},{dy}; {dx},{dy}; {dx},{dy}" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1"/>'
        anim_opac = f'<animate attributeName="opacity" values="0; 0; 1; 1; 0; 0; 0" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite"/>'
        
        g_xml = f'<g>{anim_trans}{anim_opac}<path d="{path_data}"/></g>'
        kotlin_group_svgs.append(g_xml)

    kotlin_layers_xml = "\n".join(kotlin_group_svgs)

    # --- 3. State 3: Compact Code Brackets & Slash < / > XML ---
    code_runs = generate_code_brackets_dots(grid_w, grid_h, is_dark)
    code_groups = [[] for _ in range(num_groups)]
    for run in code_runs:
        g_idx = random.randint(0, num_groups - 1)
        code_groups[g_idx].append(run)

    code_group_svgs = []
    for idx, g_runs in enumerate(code_groups):
        if not g_runs:
            continue
        path_data = "".join([f"M{rx} {ry}h{rlen}v1h-{rlen}z" if rlen > 1 else f"M{rx} {ry}h1v1h-1z" for rx, ry, rlen in g_runs])
        
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(35, 70)
        dx = int(radius * math.cos(angle))
        dy = int(radius * math.sin(angle))

        anim_trans = f'<animateTransform attributeName="transform" type="translate" values="{dx},{dy}; {dx},{dy}; {dx},{dy}; {dx},{dy}; 0,0; 0,0; {dx},{dy}" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1; .4 0 .2 1"/>'
        anim_opac = f'<animate attributeName="opacity" values="0; 0; 0; 0; 1; 1; 0" keyTimes="0; 0.230; 0.333; 0.563; 0.667; 0.897; 1" dur="17.4s" repeatCount="indefinite"/>'
        
        g_xml = f'<g>{anim_trans}{anim_opac}<path d="{path_data}"/></g>'
        code_group_svgs.append(g_xml)

    code_layers_xml = "\n".join(code_group_svgs)

    dot_color = "#A78BFA" if is_dark else "#7C3AED"
    bg_fill = "#0A101F" if is_dark else "#FFFFFF"
    window_fill = "#070B16" if is_dark else "#F1F5F9"
    panel_bg = "url(#panelGrad)" if is_dark else "#F8FAFC"
    border_stroke = "rgba(34,211,238,0.35)" if is_dark else "rgba(8,145,178,0.3)"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_label = "#22D3EE" if is_dark else "#0284C7"
    text_dim = "#94A3B8" if is_dark else "#64748B"
    text_gray = "#475569" if is_dark else "#64748B"
    dot_leader = "rgba(148,163,184,0.35)" if is_dark else "#CBD5E1"
    
    scale_x = 1.2400
    scale_y = 1.4471

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Shariar Ahamed — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A101F"/><stop offset="1" stop-color="#0C1426"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>

<!-- STRICT BOX BOUNDARY CLIPPATH -->
<clipPath id="boxClip"><rect x="36" y="84" width="400" height="492"/></clipPath>
</defs>

<rect x="2" y="2" width="1176" height="606" rx="18" fill="{window_fill}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="{panel_bg}"/>
<rect x="2" y="2" width="1176" height="46" fill="{'#0B1222' if is_dark else '#E2E8F0'}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="rgba(255,255,255,0.10)"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{text_dim}">shariaralways@gmail.com - % ./profile.sh --live</text>

<!-- VISUAL.MAP Header (Subtle Gray Color #475569) -->
<text x="38" y="74" font-size="11" font-weight="600" letter-spacing="3" fill="{text_gray}">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" fill="{bg_fill}" stroke="{border_stroke}"/>

<!-- Cyan Corner Brackets DIRECTLY ON TOP OF BOX BORDER (Zero Gap) -->
<path d="M 36 106 L 36 84 L 58 84" fill="none" stroke="#22D3EE" stroke-width="3.5" stroke-linecap="square"/>
<path d="M 414 84 L 436 84 L 436 106" fill="none" stroke="#22D3EE" stroke-width="3.5" stroke-linecap="square"/>
<path d="M 36 554 L 36 576 L 58 576" fill="none" stroke="#22D3EE" stroke-width="3.5" stroke-linecap="square"/>
<path d="M 414 576 L 436 576 L 436 554" fill="none" stroke="#22D3EE" stroke-width="3.5" stroke-linecap="square"/>

<!-- EXACT 4-SECOND STAY DURATION PER STATE MORPHING ANIMATION LOOP -->
<g clip-path="url(#boxClip)">
  <g transform="translate(50,86) scale({scale_x},{scale_y})" fill="{dot_color}" shape-rendering="crispEdges">
    <!-- State 1: Shariar's Portrait (4.0s stay) -->
{portrait_layers_xml}
    
    <!-- State 2: Kotlin Logo Symbol < (4.0s stay) -->
{kotlin_layers_xml}

    <!-- State 3: Compact Code Brackets & Slash Symbol < / > (4.0s stay) -->
{code_layers_xml}
  </g>
</g>

<!-- SYSTEM.INFO Header (Larger font-size 15px bold cyan) -->
<text x="470" y="74" font-size="15" font-weight="700" letter-spacing="2" fill="{text_label}">SYSTEM.INFO</text>
<line x1="600" y1="70" x2="1061" y2="70" stroke="rgba(255,255,255,0.10)"/>

<!-- 1. BLINKING RED • LIVE BADGE AT TOP RIGHT -->
<text x="1125" y="74" text-anchor="end" font-size="12" fill="#F87171" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>

<!-- Email Pill Header -->
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="98" width="245" height="24" rx="4" fill="#4C1D95"/>
<text x="479" y="115" font-size="13" font-weight="700" fill="#E9D5FF">shariaralways@gmail.com</text>
<line x1="725" y1="110" x2="1125" y2="110" stroke="rgba(255,255,255,0.10)"/>
</g>

<!-- Staggered Animated Data Rows (font-size 13px) -->
<g font-size="13" xml:space="preserve">
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="0.90s" fill="freeze"/><text x="470" y="142" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Subject </tspan><tspan fill="{dot_leader}">............................................................</tspan><tspan fill="{text_primary}" font-weight="600"> Shariar Ahamed</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.02s" fill="freeze"/><text x="470" y="165" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Role </tspan><tspan fill="{dot_leader}">.....................................................</tspan><tspan fill="{text_primary}" font-weight="600"> Full-Stack Developer</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.14s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.14s" fill="freeze"/><text x="470" y="188" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Origin </tspan><tspan fill="{dot_leader}">.....................................................</tspan><tspan fill="{text_primary}" font-weight="600"> Dhaka, Bangladesh</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.26s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.26s" fill="freeze"/><text x="470" y="211" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Education </tspan><tspan fill="{dot_leader}">..........................................................</tspan><tspan fill="{text_primary}" font-weight="600"> BSc in CSE</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.38s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.38s" fill="freeze"/><text x="470" y="234" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Status </tspan><tspan fill="{dot_leader}">.........................................</tspan><tspan fill="{text_primary}" font-weight="600"> Building + Learning + Shipping</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.50s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.50s" fill="freeze"/><text x="470" y="257" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">ToolChain </tspan><tspan fill="{dot_leader}">.................................</tspan><tspan fill="{text_primary}" font-weight="600"> VS Code, Git, Docker, Figma</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.72s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.72s" fill="freeze"/><text x="470" y="288" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Core.Lang </tspan><tspan fill="{dot_leader}">...................................................</tspan><tspan fill="{text_primary}" font-weight="600"> C++, Java, JavaScript, C</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.84s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.84s" fill="freeze"/><text x="470" y="311" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Core.Frontend </tspan><tspan fill="{dot_leader}">.........................................................</tspan><tspan fill="{text_primary}" font-weight="600"> HTML, CSS, Tailwind, React, Next.js</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.96s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.96s" fill="freeze"/><text x="470" y="334" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Core.Backend </tspan><tspan fill="{dot_leader}">..........................................................</tspan><tspan fill="{text_primary}" font-weight="600"> Node.js, Express</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.08s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.08s" fill="freeze"/><text x="470" y="357" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Core.Database </tspan><tspan fill="{dot_leader}">...............................................</tspan><tspan fill="{text_primary}" font-weight="600"> Firebase, MongoDB</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.20s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.20s" fill="freeze"/><text x="470" y="380" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Core.Infra </tspan><tspan fill="{dot_leader}">................................................</tspan><tspan fill="{text_primary}" font-weight="600"> Vercel, Docker, Git</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.42s" fill="freeze"/><text x="470" y="411" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="#94A3B8">- Contact </tspan><tspan fill="{dot_leader}">---------------------------------------------------------------------</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.54s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.54s" fill="freeze"/><text x="470" y="434" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Grid.Mail </tspan><tspan fill="{dot_leader}">.........................................</tspan><tspan fill="{text_primary}" font-weight="600"> shariaralways@gmail.com</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.66s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.66s" fill="freeze"/><text x="470" y="457" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Grid.Portfolio </tspan><tspan fill="{dot_leader}">....................................................</tspan><tspan fill="{text_primary}" font-weight="600"> shariarahamed.me</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.78s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.78s" fill="freeze"/><text x="470" y="480" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Grid.LinkedIn </tspan><tspan fill="{dot_leader}">............................................</tspan><tspan fill="{text_primary}" font-weight="600"> shariarahamed</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.90s" fill="freeze"/><text x="470" y="503" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Grid.GitHub </tspan><tspan fill="{dot_leader}">.........................................................</tspan><tspan fill="{text_primary}" font-weight="600"> @Shariar-Ahamed</tspan></text></g>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="3.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="3.02s" fill="freeze"/><text x="470" y="526" font-size="13" textLength="655" lengthAdjust="spacingAndGlyphs"><tspan fill="{text_label}" font-weight="700">Grid.Facebook </tspan><tspan fill="{dot_leader}">......................................................</tspan><tspan fill="{text_primary}" font-weight="600"> @shahriar.thebrowncat</tspan></text></g>
</g>

<!-- 2. BLINKING CYAN TERMINAL CURSOR AT BOTTOM PROMPT -->
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="567" font-size="13" fill="#94A3B8">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="#22D3EE">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>
</g>

<!-- ANIMATED MULTI-COLOR GRADIENT BORDER WITH GLOW FILTER -->
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>'''

    with open(output_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"{output_svg} generated with exact 4.0s stay duration per state!")

if __name__ == '__main__':
    build_arif_style_svg('F_Formal.png', 'dark.svg', is_dark=True)
    build_arif_style_svg('F_Formal.png', 'light.svg', is_dark=False)
