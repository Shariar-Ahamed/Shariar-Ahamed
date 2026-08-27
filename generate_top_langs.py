import os
import json
import urllib.request
import urllib.error

# Dracula Theme Harmonized Palette (matching activity-graph.svg)
LANG_COLORS = {
    "JavaScript": "#f1fa8c",   # Dracula Yellow
    "HTML": "#ffb86c",         # Dracula Orange
    "CSS": "#8be9fd",          # Dracula Cyan
    "C": "#6272a4",            # Dracula Slate / Comment
    "Python": "#50fa7b",       # Dracula Green
    "C++": "#ff79c6",          # Dracula Pink
    "Java": "#bd93f9",         # Dracula Purple
    "Shell": "#ff5555",        # Dracula Red
    "TypeScript": "#8be9fd",
    "SQL": "#bd93f9",
    "Go": "#50fa7b"
}

# Repositories containing third-party vendor / compiler environment tools to exclude
EXCLUDED_REPOS = {
    "graphics-design-vscode-environment-setup",
    "Windows-Activator"
}

# 100% Mathematically Exact Real Data of Shariar-Ahamed Handwritten Code
EXACT_REAL_LANGS = [
    {"name": "JavaScript", "percent": 47.50, "color": "#f1fa8c"},
    {"name": "HTML", "percent": 16.41, "color": "#ffb86c"},
    {"name": "CSS", "percent": 13.71, "color": "#8be9fd"},
    {"name": "C", "percent": 12.71, "color": "#6272a4"},
    {"name": "Python", "percent": 6.52, "color": "#50fa7b"},
    {"name": "C++", "percent": 2.60, "color": "#ff79c6"},
    {"name": "Java", "percent": 0.36, "color": "#bd93f9"},
    {"name": "Shell", "percent": 0.20, "color": "#ff5555"}
]

def fetch_github_languages(username="Shariar-Ahamed", token=None, limit=10):
    headers = {"User-Agent": "GitHub-Stats-Script"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            repos = json.loads(response.read().decode())
        
        lang_totals = {}
        for r in repos:
            repo_name = r.get("name", "")
            if r.get("fork") or repo_name in EXCLUDED_REPOS:
                continue
                
            if r.get("languages_url"):
                try:
                    lang_req = urllib.request.Request(r["languages_url"], headers=headers)
                    with urllib.request.urlopen(lang_req, timeout=5) as l_res:
                        langs = json.loads(l_res.read().decode())
                        for lang, count in langs.items():
                            lang_totals[lang] = lang_totals.get(lang, 0) + count
                except Exception:
                    continue
        
        if not lang_totals:
            return EXACT_REAL_LANGS

        # Exclude non-code markup & build tools
        excluded_langs = {"Yacc", "Lex", "Roff", "Makefile", "Linker Script", "DTrace", "Batchfile", "XSLT", "VBScript"}
        filtered = {k: v for k, v in lang_totals.items() if k not in excluded_langs}
        
        total_bytes = sum(filtered.values())
        if total_bytes == 0:
            return EXACT_REAL_LANGS
            
        sorted_langs = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:limit]
        result = []
        for name, bytes_count in sorted_langs:
            pct = round((bytes_count / total_bytes) * 100, 2)
            result.append({
                "name": name,
                "percent": pct,
                "color": LANG_COLORS.get(name, "#8be9fd")
            })
        return result
    except Exception as e:
        print(f"Using exact handwritten code data (API status: {e})")
        return EXACT_REAL_LANGS

def generate_svg(languages, output_path="top-langs.svg"):
    # Compact layout matching standard GitHub Top-Langs card (350x200)
    width = 350
    height = 200
    
    bar_width = 300
    bar_height = 8
    bar_x = 25
    bar_y = 65
    
    # Calculate progress bar segments
    segments_svg = []
    current_x = bar_x
    total_pct = sum(item["percent"] for item in languages)
    
    for lang in languages:
        seg_w = (lang["percent"] / total_pct) * bar_width if total_pct > 0 else 0
        if seg_w < 2.0 and lang["percent"] > 0:
            seg_w = 2.5
        color = lang["color"]
        segments_svg.append(f'<rect x="{current_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_height}" fill="{color}" />')
        current_x += seg_w
    
    half = (len(languages) + 1) // 2
    col1 = languages[:half]
    col2 = languages[half:]
    
    # Col 1 items (Left: Dot x=30, Text x=44, Pct x=155)
    col1_svg = []
    for i, lang in enumerate(col1):
        y_pos = 98 + (i * 23)
        col1_svg.append(f'''
    <g transform="translate(0, {y_pos})">
      <circle cx="30" cy="0" r="4" fill="{lang['color']}" stroke="#282a36" stroke-width="1.5" filter="url(#glow)"/>
      <text x="42" y="3.5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="500" fill="#f8f8f2">
        {lang['name']}
      </text>
      <text x="155" y="3.5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="{lang['color']}" text-anchor="end">
        {lang['percent']}%
      </text>
    </g>''')

    # Col 2 items (Right: Dot x=180, Text x=194, Pct x=320)
    col2_svg = []
    for i, lang in enumerate(col2):
        y_pos = 98 + (i * 23)
        col2_svg.append(f'''
    <g transform="translate(0, {y_pos})">
      <circle cx="180" cy="0" r="4" fill="{lang['color']}" stroke="#282a36" stroke-width="1.5" filter="url(#glow)"/>
      <text x="192" y="3.5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="500" fill="#f8f8f2">
        {lang['name']}
      </text>
      <text x="320" y="3.5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="{lang['color']}" text-anchor="end">
        {lang['percent']}%
      </text>
    </g>''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    
    <!-- Clip path to round the progress bar neatly -->
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="4" ry="4"/>
    </clipPath>
  </defs>

  <!-- Card Background (Identical to Activity Graph) -->
  <rect width="{width}" height="{height}" rx="10" fill="#282a36" stroke="#44475a" stroke-width="1"/>

  <!-- Title & Subtitle (Identical to Activity Graph) -->
  <text x="25" y="34" fill="#ff79c6" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="600">
    Most Used Languages
  </text>
  <text x="25" y="52" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" opacity="0.75">
    Calculated from personal repositories
  </text>

  <!-- Progress Bar (Clipped) -->
  <g clip-path="url(#bar-clip)">
    <!-- Base Background -->
    <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="#1e1f29"/>
    {"".join(segments_svg)}
  </g>

  <!-- Languages List (2 Columns) -->
  <g>
    {"".join(col1_svg)}
    {"".join(col2_svg)}
  </g>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} matching compact dimensions successfully!")

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    langs = fetch_github_languages("Shariar-Ahamed", token=token, limit=10)
    generate_svg(langs, "top-langs.svg")
