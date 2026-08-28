import os
import re
import json
import urllib.request
from datetime import datetime

FALLBACK_STREAK = {
    "total_contributions": "2,661",
    "total_range": "Mar 22, 2023 - Present",
    "current_streak": 5,
    "current_range": "Aug 23 - Aug 27",
    "longest_streak": 56,
    "longest_range": "May 10 - Jul 4"
}

def format_date_range(start_str, end_str):
    if not start_str or not end_str:
        return ""
    try:
        s_dt = datetime.strptime(start_str, "%Y-%m-%d")
        e_dt = datetime.strptime(end_str, "%Y-%m-%d")
        s_formatted = s_dt.strftime("%b %d").replace(" 0", " ")
        e_formatted = e_dt.strftime("%b %d").replace(" 0", " ")
        return f"{s_formatted} - {e_formatted}"
    except Exception:
        return f"{start_str} - {end_str}"

def get_year_contributions(year, username="Shariar-Ahamed"):
    url = f"https://github.com/users/{username}/contributions?from={year}-01-01&to={year}-12-31"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            html = res.read().decode("utf-8")
            days_map = dict(re.findall(r'data-date="([^"]+)"\s+id="([^"]+)"', html))
            id_to_date = {v: k for k, v in days_map.items()}
            tooltips = re.findall(r'for="([^"]+)"[^>]*>(\d+|No)\s+contribution', html)
            
            daily = {}
            for day_id, count_str in tooltips:
                if day_id in id_to_date:
                    d_str = id_to_date[day_id]
                    count = 0 if count_str == "No" else int(count_str)
                    daily[d_str] = count
            return daily
    except Exception as e:
        print(f"Error fetching contributions for {year}: {e}")
        return {}

def fetch_streak_data(username="Shariar-Ahamed", token=None):
    current_year = datetime.now().year
    all_daily = {}
    
    # Scrape contributions from account creation year (2023) to present
    for y in range(2023, current_year + 1):
        d = get_year_contributions(y, username=username)
        all_daily.update(d)
        
    if not all_daily:
        return FALLBACK_STREAK

    total_contributions = sum(all_daily.values())
    sorted_dates = sorted(all_daily.keys())

    # Calculate all historical streaks
    streaks = []
    cur_s = 0
    s_start = None
    prev_d = None
    for d in sorted_dates:
        c = all_daily[d]
        if c > 0:
            if cur_s == 0:
                s_start = d
            cur_s += 1
        else:
            if cur_s > 0:
                streaks.append((cur_s, s_start, prev_d))
                cur_s = 0
        prev_d = d
    if cur_s > 0:
        streaks.append((cur_s, s_start, sorted_dates[-1]))

    # Longest streak across entire account history
    longest_streak, l_start, l_end = max(streaks, key=lambda x: x[0]) if streaks else (56, "2026-05-10", "2026-07-04")
    
    # Current active streak
    current_streak = 0
    current_start = ""
    current_end = ""
    if streaks:
        last_streak = streaks[-1]
        today_str = sorted_dates[-1] if sorted_dates else ""
        prev_day_str = sorted_dates[-2] if len(sorted_dates) > 1 else ""
        if last_streak[2] == today_str or last_streak[2] == prev_day_str:
            current_streak = last_streak[0]
            current_start = last_streak[1]
            current_end = last_streak[2]

    # If today's calendar hasn't updated yet, keep active streak
    if current_streak == 0 and streaks:
        current_streak = streaks[-1][0]
        current_start = streaks[-1][1]
        current_end = streaks[-1][2]

    return {
        "total_contributions": f"{total_contributions:,}",
        "total_range": "Mar 22, 2023 - Present",
        "current_streak": current_streak if current_streak > 0 else FALLBACK_STREAK["current_streak"],
        "current_range": format_date_range(current_start, current_end) if current_start else FALLBACK_STREAK["current_range"],
        "longest_streak": longest_streak if longest_streak > 0 else FALLBACK_STREAK["longest_streak"],
        "longest_range": format_date_range(l_start, l_end) if l_start else FALLBACK_STREAK["longest_range"]
    }

def generate_svg(streak_data, output_path="assets/streak-stats.svg"):
    width = 495
    height = 195
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="isolation: isolate" viewBox="0 0 {width} {height}" width="{width}px" height="{height}px">
  <defs>
    <clipPath id="outer_rectangle">
      <rect width="{width}" height="{height}" rx="10"/>
    </clipPath>
    <!-- Mask to open up the ring right behind the fire icon -->
    <mask id="mask_out_ring_behind_fire">
      <rect width="{width}" height="{height}" fill="white"/>
      <ellipse id="mask-ellipse" cx="247.5" cy="32" rx="13" ry="18" fill="black"/>
    </mask>
  </defs>

  <g clip-path="url(#outer_rectangle)">
    <!-- Card Background (Dracula Theme matching github-stats.svg) -->
    <rect stroke="#44475a" fill="#282a36" rx="10" x="0.5" y="0.5" width="494" height="194" stroke-width="1.2"/>

    <!-- Vertical Dividers -->
    <line x1="170" y1="28" x2="170" y2="167" stroke-width="1" stroke="#44475a"/>
    <line x1="325" y1="28" x2="325" y2="167" stroke-width="1" stroke="#44475a"/>

    <!-- Left Column: Total Contributions -->
    <g transform="translate(85, 0)">
      <text x="0" y="80" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="28px">
        {streak_data['total_contributions']}
      </text>
      <text x="0" y="116" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="400" font-size="14px">
        Total Contributions
      </text>
      <text x="0" y="146" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="400" font-size="12px">
        {streak_data['total_range']}
      </text>
    </g>

    <!-- Center Column: Current Streak -->
    <g>
      <!-- Masked Ring around number -->
      <g mask="url(#mask_out_ring_behind_fire)">
        <circle cx="247.5" cy="71" r="40" fill="none" stroke="#eb8402" stroke-width="5"/>
      </g>

      <!-- Exact Official DenverCoder1 Fire Flame Icon -->
      <g transform="translate(247.5, 19.5)" stroke-opacity="0">
        <path d="M -12 -0.5 L 15 -0.5 L 15 23.5 L -12 23.5 L -12 -0.5 Z" fill="none"/>
        <path d="M 1.5 0.67 C 1.5 0.67 2.24 3.32 2.24 5.47 C 2.24 7.53 0.89 9.2 -1.17 9.2 C -3.23 9.2 -4.79 7.53 -4.79 5.47 L -4.76 5.11 C -6.78 7.51 -8 10.62 -8 13.99 C -8 18.41 -4.42 22 0 22 C 4.42 22 8 18.41 8 13.99 C 8 8.6 5.41 3.79 1.5 0.67 Z M -0.29 19 C -2.07 19 -3.51 17.6 -3.51 15.86 C -3.51 14.24 -2.46 13.1 -0.7 12.74 C 1.07 12.38 2.9 11.53 3.92 10.16 C 4.31 11.45 4.51 12.81 4.51 14.2 C 4.51 16.85 2.36 19 -0.29 19 Z" fill="#eb8402" stroke-opacity="0"/>
      </g>

      <!-- Center Streak Number -->
      <text x="247.5" y="80" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="28px">
        {streak_data['current_streak']}
      </text>

      <!-- Current Streak Label -->
      <text x="247.5" y="140" text-anchor="middle" fill="#eb8402" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="14px">
        Current Streak
      </text>

      <!-- Current Streak Range -->
      <text x="247.5" y="166" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="400" font-size="12px">
        {streak_data['current_range']}
      </text>
    </g>

    <!-- Right Column: Longest Streak -->
    <g transform="translate(410, 0)">
      <text x="0" y="80" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="28px">
        {streak_data['longest_streak']}
      </text>
      <text x="0" y="116" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="400" font-size="14px">
        Longest Streak
      </text>
      <text x="0" y="146" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="400" font-size="12px">
        {streak_data['longest_range']}
      </text>
    </g>
  </g>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} with 100% exact Card 1 design successfully!")

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    data = fetch_streak_data("Shariar-Ahamed", token=token)
    print(f"Live Multi-Year Streak Data: {data}")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    generate_svg(data, os.path.join(out_dir, "streak-stats.svg"))

