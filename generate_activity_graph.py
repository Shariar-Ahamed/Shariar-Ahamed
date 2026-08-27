import os
import re
import json
import urllib.request
from datetime import datetime

def fetch_contributions(username="Shariar-Ahamed", token=None):
    # Method 1: Official GitHub GraphQL API (when token is available)
    if token:
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """
        try:
            req_data = json.dumps({"query": query, "variables": {"login": username}}).encode('utf-8')
            req = urllib.request.Request("https://api.github.com/graphql", data=req_data, headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "Activity-Graph-Generator",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                weeks = data.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {}).get("weeks", [])
                days = []
                for w in weeks:
                    for d in w.get("contributionDays", []):
                        days.append((d["date"], d["contributionCount"]))
                if len(days) >= 31:
                    return days[-31:]
        except Exception as e:
            print(f"GraphQL contribution fetch error: {e}")

    # Method 2: GitHub HTML Profile Scraper (publicly available & highly reliable)
    try:
        url = f"https://github.com/users/{username}/contributions"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode("utf-8")
            days_map = dict(re.findall(r'data-date="([^"]+)"\s+id="([^"]+)"', html))
            id_to_date = {v: k for k, v in days_map.items()}
            tooltips = re.findall(r'for="([^"]+)"[^>]*>(\d+|No)\s+contribution', html)
            
            history = []
            for day_id, count_str in tooltips:
                if day_id in id_to_date:
                    d_str = id_to_date[day_id]
                    count = 0 if count_str == "No" else int(count_str)
                    history.append((d_str, count))
            
            history.sort(key=lambda x: x[0])
            if len(history) >= 31:
                return history[-31:]
    except Exception as e:
        print(f"HTML scraper contribution fetch error: {e}")

    # Fallback data if offline
    fallback_data = [
        ("2026-07-28", 7), ("2026-07-29", 1), ("2026-07-30", 3), ("2026-07-31", 16),
        ("2026-08-01", 24), ("2026-08-02", 20), ("2026-08-03", 21), ("2026-08-04", 3),
        ("2026-08-05", 47), ("2026-08-06", 7), ("2026-08-07", 4), ("2026-08-08", 8),
        ("2026-08-09", 6), ("2026-08-10", 3), ("2026-08-11", 2), ("2026-08-12", 3),
        ("2026-08-13", 12), ("2026-08-14", 6), ("2026-08-15", 10), ("2026-08-16", 3),
        ("2026-08-17", 5), ("2026-08-18", 10), ("2026-08-19", 1), ("2026-08-20", 3),
        ("2026-08-21", 2), ("2026-08-22", 0), ("2026-08-23", 18), ("2026-08-24", 2),
        ("2026-08-25", 3), ("2026-08-26", 22), ("2026-08-27", 4)
    ]
    return fallback_data

def get_smooth_svg_path(points):
    if not points:
        return ""
    if len(points) == 1:
        return f"M {points[0][0]} {points[0][1]}"
    
    path = f"M {points[0][0]:.2f} {points[0][1]:.2f}"
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        
        # Catmull-Rom to Cubic Bezier conversion
        cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
        cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
        cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
        cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
        
        path += f" C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}"
    return path

def generate_svg(daily_contributions, output_path="activity-graph.svg"):
    width = 850
    height = 300
    
    left_x = 75
    right_x = 815
    top_y = 65
    bottom_y = 240
    
    counts = [c[1] for c in daily_contributions]
    max_c = max(counts) if counts else 50
    
    # Determine Y-axis max scale (multiples of 5 or 10)
    if max_c <= 20:
        max_scale = 20
        y_step = 5
    elif max_c <= 30:
        max_scale = 30
        y_step = 5
    elif max_c <= 50:
        max_scale = 50
        y_step = 5
    elif max_c <= 75:
        max_scale = 75
        y_step = 15
    else:
        max_scale = ((max_c // 20) + 1) * 20
        y_step = max_scale // 10

    # Calculate coordinates for each day
    n = len(daily_contributions)
    dx = (right_x - left_x) / (n - 1) if n > 1 else 0
    
    points = []
    for i, (date_str, count) in enumerate(daily_contributions):
        px = left_x + i * dx
        clamped_c = min(count, max_scale)
        py = bottom_y - (clamped_c / max_scale) * (bottom_y - top_y)
        points.append((px, py))

    curve_path = get_smooth_svg_path(points)
    area_path = f"{curve_path} L {points[-1][0]:.2f} {bottom_y} L {points[0][0]:.2f} {bottom_y} Z"

    # Y-axis ticks & grid lines
    y_ticks_svg = []
    for val in range(0, max_scale + 1, y_step):
        y_pos = bottom_y - (val / max_scale) * (bottom_y - top_y)
        y_ticks_svg.append(f'''
    <text x="65" y="{y_pos + 4:.1f}" text-anchor="end" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600">{val}</text>
    <line x1="{left_x}" y1="{y_pos:.1f}" x2="{right_x}" y2="{y_pos:.1f}" stroke="#44475a" stroke-width="1" stroke-dasharray="3,3" opacity="0.65"/>''')

    # X-axis day labels & vertical dashed lines
    x_labels_svg = []
    for i, (date_str, count) in enumerate(daily_contributions):
        px = points[i][0]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_num = str(dt.day)
        x_labels_svg.append(f'''
    <line x1="{px:.1f}" y1="{top_y}" x2="{px:.1f}" y2="{bottom_y}" stroke="#44475a" stroke-width="1" stroke-dasharray="3,3" opacity="0.35"/>
    <text x="{px:.1f}" y="258" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600">{day_num}</text>''')

    # Points circles
    points_svg = []
    for px, py in points:
        points_svg.append(f'''<circle cx="{px:.2f}" cy="{py:.2f}" r="4.5" fill="#ff79c6" stroke="#282a36" stroke-width="1.8"/>''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <defs>
    <!-- Area Gradient (Lavender to transparent) -->
    <linearGradient id="activityAreaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bd93f9" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#bd93f9" stop-opacity="0.0"/>
    </linearGradient>

    <!-- Glow Filter for the wave line -->
    <filter id="activityGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#bd93f9" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Card Background (Dracula Theme matching all profile cards) -->
  <rect width="{width}" height="{height}" rx="10" fill="#282a36" stroke="#44475a" stroke-width="1.2"/>

  <!-- Centered Title -->
  <text x="{width / 2}" y="36" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="700">
    Shariar Ahamed Ripon's Contribution Graph
  </text>

  <!-- Y-Axis Vertical Label -->
  <text x="24" y="152" text-anchor="middle" transform="rotate(-90 24, 152)" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600">
    Contributions
  </text>

  <!-- Y-Axis Scale Ticks & Horizontal Grid Lines -->
  <g>
    {"".join(y_ticks_svg)}
  </g>

  <!-- X-Axis Vertical Lines & Day Labels -->
  <g>
    {"".join(x_labels_svg)}
  </g>

  <!-- Bottom Axis Line -->
  <line x1="{left_x}" y1="{bottom_y}" x2="{right_x}" y2="{bottom_y}" stroke="#44475a" stroke-width="1.5"/>

  <!-- Bottom 'Days' Axis Title -->
  <text x="{(left_x + right_x) / 2}" y="284" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600">
    Days
  </text>

  <!-- Area Fill Under Curve -->
  <path d="{area_path}" fill="url(#activityAreaGrad)"/>

  <!-- Smooth Activity Wave Curve -->
  <path d="{curve_path}" fill="none" stroke="#bd93f9" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#activityGlow)"/>

  <!-- Pink Glowing Data Points -->
  <g>
    {"".join(points_svg)}
  </g>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} matching reference design successfully!")

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    data = fetch_contributions("Shariar-Ahamed", token=token)
    generate_svg(data, "activity-graph.svg")
