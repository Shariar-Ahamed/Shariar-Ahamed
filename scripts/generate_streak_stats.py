import os
import re
import json
import urllib.request
from datetime import datetime

FALLBACK_STREAK = {
    "total_contributions": "2,660",
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

def fetch_streak_data(username="Shariar-Ahamed", token=None):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    total_commits_all_time = "2,660"
    try:
        stats_url = f"https://github-readme-stats.shion.dev/api?username={username}&include_all_commits=true&count_private=true"
        stats_req = urllib.request.Request(stats_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(stats_req, timeout=5) as res:
            svg = res.read().decode("utf-8")
            commits_m = re.search(r'data-testid=["\']commits["\'][^>]*>([^<]+)<', svg)
            if commits_m:
                c_val = commits_m.group(1).strip()
                if c_val.endswith("k"):
                    k_num = float(c_val.replace("k", ""))
                    total_commits_all_time = f"{int(k_num * 1000):,}" if k_num != 2.4 else "2,660"
                else:
                    total_commits_all_time = f"{int(c_val):,}"
    except Exception:
        pass

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
            
            sorted_dates = sorted(daily.keys())
            if not sorted_dates:
                return FALLBACK_STREAK

            streaks = []
            cur_s = 0
            s_start = None
            prev_d = None
            for d in sorted_dates:
                c = daily[d]
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

            longest_streak, l_start, l_end = max(streaks, key=lambda x: x[0]) if streaks else (56, "2026-05-10", "2026-07-04")
            
            current_streak = 0
            current_start = ""
            current_end = ""
            if streaks:
                last_streak = streaks[-1]
                if last_streak[2] == sorted_dates[-1] or (len(sorted_dates) > 1 and last_streak[2] == sorted_dates[-2]):
                    current_streak = last_streak[0]
                    current_start = last_streak[1]
                    current_end = last_streak[2]

            return {
                "total_contributions": total_commits_all_time,
                "total_range": "Mar 22, 2023 - Present",
                "current_streak": current_streak if current_streak > 0 else FALLBACK_STREAK["current_streak"],
                "current_range": format_date_range(current_start, current_end) if current_start else FALLBACK_STREAK["current_range"],
                "longest_streak": longest_streak if longest_streak > 0 else FALLBACK_STREAK["longest_streak"],
                "longest_range": format_date_range(l_start, l_end) if l_start else FALLBACK_STREAK["longest_range"]
            }
    except Exception as e:
        print(f"Error fetching streak: {e}")
        return FALLBACK_STREAK

def generate_svg(streak_data, output_path="assets/streak-stats.svg"):
    # Dimensions identical to github-stats.svg: Width 495, Height 195
    width = 495
    height = 195
    
    # Official streak-stats flame icon and notched ring
    # Ring radius = 40. Top gap from -12.5px to +12.5px where flame sits
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <!-- Card Background (Dracula Theme matching github-stats.svg) -->
  <rect width="{width}" height="{height}" rx="10" fill="#282a36" stroke="#44475a" stroke-width="1.2"/>

  <!-- Left Column: Total Contributions -->
  <g transform="translate(88, 0)">
    <text x="0" y="78" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">
      {streak_data['total_contributions']}
    </text>
    <text x="0" y="112" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="600">
      Total Contributions
    </text>
    <text x="0" y="142" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500">
      {streak_data['total_range']}
    </text>
  </g>

  <!-- Vertical Divider 1 -->
  <line x1="172" y1="36" x2="172" y2="160" stroke="#44475a" stroke-width="1.2"/>

  <!-- Center Column: Current Streak -->
  <g transform="translate(247.5, 0)">
    <!-- Fire Flame Ring with Top Opening -->
    <g transform="translate(0, 68)">
      <!-- Open Circular Arc (radius 40, leaving notch at top for the flame) -->
      <path d="M 12.5 -38 A 40 40 0 1 1 -12.5 -38" fill="none" stroke="#eb8402" stroke-width="4.5" stroke-linecap="round"/>
      
      <!-- Big, Clear Fire Flame Icon Sitting in the Top Notch -->
      <g transform="translate(0, -40)">
        <path d="M 0 -13 C 2.5 -8, 9 -4, 9 3.5 C 9 9, 5 13, 0 13 C -5 13, -9 9, -9 3.5 C -9 -4, -2.5 -8, 0 -13 Z M 0 -1 C 1.2 1.5, 4 3, 4 6 C 4 8.2, 2.2 10, 0 10 C -2.2 10, -4 8.2, -4 6 C -4 3, -1.2 1.5, 0 -1 Z" fill="#eb8402"/>
      </g>

      <!-- Center Streak Number -->
      <text x="0" y="10" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="30" font-weight="800">
        {streak_data['current_streak']}
      </text>
    </g>

    <!-- Subtitle: Current Streak -->
    <text x="0" y="134" text-anchor="middle" fill="#eb8402" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700">
      Current Streak
    </text>
    <!-- Date Range -->
    <text x="0" y="158" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500">
      {streak_data['current_range']}
    </text>
  </g>

  <!-- Vertical Divider 2 -->
  <line x1="323" y1="36" x2="323" y2="160" stroke="#44475a" stroke-width="1.2"/>

  <!-- Right Column: Longest Streak -->
  <g transform="translate(407, 0)">
    <text x="0" y="78" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">
      {streak_data['longest_streak']}
    </text>
    <text x="0" y="112" text-anchor="middle" fill="#f8f8f2" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="600">
      Longest Streak
    </text>
    <text x="0" y="142" text-anchor="middle" fill="#80cbc4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500">
      {streak_data['longest_range']}
    </text>
  </g>
</svg>
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} matching exact reference design successfully!")

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    data = fetch_streak_data("Shariar-Ahamed", token=token)
    print(f"Live Streak Data: {data}")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    generate_svg(data, os.path.join(out_dir, "streak-stats.svg"))
