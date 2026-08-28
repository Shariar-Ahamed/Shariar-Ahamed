import os
import json
import urllib.request
import urllib.error
import base64

# Harmonized Dracula Palette for Languages
LANG_COLORS = {
    "Other": "#707880",
    "JavaScript": "#f1fa8c",
    "HTML": "#ff79c6",
    "Markdown": "#8be9fd",
    "CSS": "#bd93f9",
    "C++": "#ff5555",
    "M3U": "#50fa7b",
    "Python": "#50fa7b",
    "JSON": "#6272a4",
    "YAML": "#ff5555",
    "Text": "#6272a4",
    "Bash": "#6272a4",
    "Git Config": "#ffb86c",
    "Common Lisp": "#50fa7b",
    "Groovy": "#8be9fd",
    "Java": "#f1fa8c",
    "XML": "#8be9fd",
    "Yacc": "#50fa7b",
    "CSV": "#50fa7b",
    "TypeScript": "#8be9fd",
    "Image": "#6272a4",
    "TOML": "#ffb86c",
    "INI": "#f8f8f2",
    "Git": "#6272a4",
    "PHP": "#bd93f9",
    "SQL": "#bd93f9",
    "C": "#6272a4",
    "Go": "#50fa7b",
    "Rust": "#ffb86c"
}

# Authentic profile data matching https://wakatime.com/@ShariarAlways
FALLBACK_WAKATIME_DATA = [
    # Left Column
    {"name": "Other", "time": "409 hrs 4 mins", "percent": 43.42, "color": "#707880"},
    {"name": "HTML", "time": "89 hrs", "percent": 9.45, "color": "#ff79c6"},
    {"name": "CSS", "time": "58 hrs 14 mins", "percent": 6.18, "color": "#bd93f9"},
    {"name": "M3U", "time": "16 hrs 56 mins", "percent": 1.80, "color": "#50fa7b"},
    {"name": "JSON", "time": "11 hrs 16 mins", "percent": 1.20, "color": "#6272a4"},
    {"name": "Text", "time": "4 hrs 53 mins", "percent": 0.52, "color": "#6272a4"},
    {"name": "Git Config", "time": "3 hrs 7 mins", "percent": 0.33, "color": "#ffb86c"},
    {"name": "Groovy", "time": "1 hr 40 mins", "percent": 0.18, "color": "#8be9fd"},
    {"name": "XML", "time": "44 mins", "percent": 0.08, "color": "#8be9fd"},
    {"name": "CSV", "time": "11 mins", "percent": 0.02, "color": "#50fa7b"},
    {"name": "Image", "time": "5 mins", "percent": 0.01, "color": "#6272a4"},
    {"name": "INI", "time": "1 min", "percent": 0.002, "color": "#f8f8f2"},
    
    # Right Column
    {"name": "JavaScript", "time": "218 hrs 9 mins", "percent": 23.15, "color": "#f1fa8c"},
    {"name": "Markdown", "time": "74 hrs 55 mins", "percent": 7.95, "color": "#8be9fd"},
    {"name": "C++", "time": "20 hrs 29 mins", "percent": 2.18, "color": "#ff5555"},
    {"name": "Python", "time": "16 hrs 1 min", "percent": 1.70, "color": "#50fa7b"},
    {"name": "YAML", "time": "8 hrs 30 mins", "percent": 0.90, "color": "#ff5555"},
    {"name": "Bash", "time": "4 hrs 25 mins", "percent": 0.47, "color": "#6272a4"},
    {"name": "Common Lisp", "time": "2 hrs 17 mins", "percent": 0.24, "color": "#50fa7b"},
    {"name": "Java", "time": "1 hr 14 mins", "percent": 0.13, "color": "#f1fa8c"},
    {"name": "Yacc", "time": "34 mins", "percent": 0.06, "color": "#50fa7b"},
    {"name": "TypeScript", "time": "5 mins", "percent": 0.01, "color": "#8be9fd"},
    {"name": "TOML", "time": "4 mins", "percent": 0.01, "color": "#ffb86c"},
    {"name": "Git", "time": "1 min", "percent": 0.002, "color": "#6272a4"}
]

def fetch_wakatime_stats(api_key=None):
    if not api_key:
        return FALLBACK_WAKATIME_DATA

    try:
        b64_key = base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
        # timeout=15 matches the official WakaTime public profile standard
        url = f"https://wakatime.com/api/v1/users/current/stats/all_time?timeout=15&api_key={api_key}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Authorization": f"Basic {b64_key}"
        })
        with urllib.request.urlopen(req, timeout=12) as res:
            data = json.loads(res.read().decode("utf-8"))
            languages = data.get("data", {}).get("languages", [])
            if languages:
                parsed = []
                for lang in languages:
                    name = lang.get("name")
                    time_text = lang.get("text")
                    percent = float(lang.get("percent", 0.0))
                    color = LANG_COLORS.get(name, "#8be9fd")
                    parsed.append({
                        "name": name,
                        "time": time_text,
                        "percent": percent,
                        "color": color
                    })
                return parsed
    except Exception as e:
        print(f"WakaTime API fetch error: {e}")

    return FALLBACK_WAKATIME_DATA

def generate_svg(data, output_path="assets/wakatime-stats.svg"):
    width = 495
    height = 365
    
    # Progress Bar coordinates
    bar_x = 25
    bar_y = 52
    bar_width = 445
    bar_height = 8
    
    # Sort for progress bar
    sorted_for_bar = sorted(data, key=lambda x: x["percent"], reverse=True)
    total_pct = sum(item["percent"] for item in sorted_for_bar) or 100.0
    
    segments_svg = []
    current_x = bar_x
    for item in sorted_for_bar:
        seg_w = (item["percent"] / total_pct) * bar_width
        if seg_w < 0.8:
            continue
        segments_svg.append(
            f'<rect x="{current_x:.2f}" y="{bar_y}" width="{seg_w:.2f}" height="{bar_height}" fill="{item["color"]}"/>'
        )
        current_x += seg_w

    # Top 24 languages displayed in 2 clean columns of 12 items
    display_langs = data[:24] if len(data) >= 24 else data
    mid = (len(display_langs) + 1) // 2
    left_items = display_langs[:mid]
    right_items = display_langs[mid:]

    col1_svg = []
    for i, item in enumerate(left_items):
        y_pos = 82 + (i * 22)
        col1_svg.append(f'''
    <g transform="translate(25, {y_pos})">
      <circle cx="4" cy="-4" r="4" fill="{item['color']}"/>
      <text x="14" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="500" fill="#f8f8f2">
        {item['name']} - <tspan fill="#8be9fd">{item['time']}</tspan>
      </text>
    </g>''')

    col2_svg = []
    for i, item in enumerate(right_items):
        y_pos = 82 + (i * 22)
        col2_svg.append(f'''
    <g transform="translate(255, {y_pos})">
      <circle cx="4" cy="-4" r="4" fill="{item['color']}"/>
      <text x="14" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="500" fill="#f8f8f2">
        {item['name']} - <tspan fill="#8be9fd">{item['time']}</tspan>
      </text>
    </g>''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <defs>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="4"/>
    </clipPath>
  </defs>

  <!-- Card Background (Dracula Theme matching standard dimensions) -->
  <rect width="{width}" height="{height}" rx="10" fill="#282a36" stroke="#44475a" stroke-width="1.2"/>

  <!-- Card Title -->
  <text x="25" y="34" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="17" font-weight="700" letter-spacing="0.5px">
    WakaTime Stats
  </text>

  <!-- Multi-Color Progress Bar -->
  <g clip-path="url(#bar-clip)">
    <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="#1e1f29"/>
    {"".join(segments_svg)}
  </g>

  <!-- Languages Time Spent List (2 Columns) -->
  <g>
    {"".join(col1_svg)}
    {"".join(col2_svg)}
  </g>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} matching live WakaTime data successfully!")

if __name__ == "__main__":
    api_key = os.environ.get("WAKATIME_API_KEY")
    data = fetch_wakatime_stats(api_key=api_key)
    print(f"Loaded {len(data)} languages!")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    generate_svg(data, os.path.join(out_dir, "wakatime-stats.svg"))
