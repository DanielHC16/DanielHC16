import urllib.request
import time
import os
import sys

URLS = {
    "github-stats.svg": [
        "https://github-readme-stats.vercel.app/api?username=DanielHC16&hide_title=false&hide_rank=false&show_icons=true&include_all_commits=true&count_private=true&disable_animations=false&theme=merko&locale=en&hide_border=false&order=1&custom_title=My%20GitHub%20Stats",
        "https://github-readme-stats-eight-theta.vercel.app/api?username=DanielHC16&hide_title=false&hide_rank=false&show_icons=true&include_all_commits=true&count_private=true&disable_animations=false&theme=merko&locale=en&hide_border=false&order=1&custom_title=My%20GitHub%20Stats",
        "https://github-readme-stats.sigma-axis.vercel.app/api?username=DanielHC16&hide_title=false&hide_rank=false&show_icons=true&include_all_commits=true&count_private=true&disable_animations=false&theme=merko&locale=en&hide_border=false&order=1&custom_title=My%20GitHub%20Stats"
    ],
    "github-streak.svg": [
        "https://streak-stats.demolab.com?user=DanielHC16&locale=en&mode=daily&theme=merko&hide_border=false&border_radius=5&date_format=%5BY.%5Dn.j&order=3"
    ]
}

MAX_RETRIES = 3
RETRY_DELAY = 5 # seconds

def download_file(filename, url_list):
    print(f"Downloading {filename}...")
    
    os.makedirs("dist", exist_ok=True)
    
    # Try all mirror URLs
    for url in url_list:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Use a curl user-agent to bypass some basic bot blocks
                req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
                response = urllib.request.urlopen(req, timeout=10)
                content = response.read().decode('utf-8')
                
                if "<svg" not in content:
                    raise ValueError("Response does not look like an SVG")
                    
                with open(f"dist/{filename}", "w", encoding="utf-8") as f:
                    f.write(content)
                    
                print(f"Successfully downloaded {filename} from {url.split('/')[2]}")
                return True
                
            except Exception as e:
                print(f"Attempt {attempt}/{MAX_RETRIES} failed for {url.split('/')[2]}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
    print(f"Failed to download {filename} from all APIs. Attempting fallback to last known good version...")
    try:
        # Fallback to the current image on the output branch
        fallback_url = f"https://raw.githubusercontent.com/DanielHC16/DanielHC16/output/{filename}"
        fallback_req = urllib.request.Request(fallback_url, headers={'User-Agent': 'curl/7.68.0'})
        fallback_content = urllib.request.urlopen(fallback_req, timeout=10).read().decode('utf-8')
        with open(f"dist/{filename}", "w", encoding="utf-8") as f:
            f.write(fallback_content)
        print(f"Successfully restored {filename} from fallback.")
        return True
    except Exception as fallback_e:
        print(f"Fallback also failed (likely first run): {fallback_e}")
        
    # Absolute last resort: Generate a placeholder SVG so the README doesn't break
    print(f"Generating placeholder SVG for {filename}...")
    placeholder_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="170" viewBox="0 0 450 170">
      <rect x="0" y="0" width="450" height="170" fill="#0a0f0b" rx="5" stroke="#68b587" stroke-width="1"/>
      <text x="225" y="80" font-family="monospace" font-size="14" fill="#68b587" text-anchor="middle">GitHub API temporarily unavailable.</text>
      <text x="225" y="105" font-family="monospace" font-size="12" fill="#b7d364" text-anchor="middle">GitHub Actions will retry automatically later.</text>
    </svg>'''
    with open(f"dist/{filename}", "w", encoding="utf-8") as f:
        f.write(placeholder_svg)
        
    # Return True so the workflow never fails and pushes what it has
    return True

if __name__ == "__main__":
    for filename, urls in URLS.items():
        download_file(filename, urls)
