import urllib.request
import time
import os
import sys

URLS = {
    "github-stats.svg": "https://github-readme-stats.vercel.app/api?username=DanielHC16&hide_title=false&hide_rank=false&show_icons=true&include_all_commits=true&count_private=true&disable_animations=false&theme=merko&locale=en&hide_border=false&order=1&custom_title=My%20GitHub%20Stats",
    "github-streak.svg": "https://streak-stats.demolab.com?user=DanielHC16&locale=en&mode=daily&theme=merko&hide_border=false&border_radius=5&date_format=%5BY.%5Dn.j&order=3"
}

MAX_RETRIES = 5
RETRY_DELAY = 10 # seconds

def download_file(filename, url):
    print(f"Downloading {filename}...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            content = response.read().decode('utf-8')
            
            if "<svg" not in content:
                raise ValueError("Response does not look like an SVG")
                
            # Create dist directory if it doesn't exist
            os.makedirs("dist", exist_ok=True)
            
            with open(f"dist/{filename}", "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"Successfully downloaded {filename}")
            return True
            
        except Exception as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed for {filename}: {e}")
            if attempt < MAX_RETRIES:
                print(f"Waiting {RETRY_DELAY} seconds before retrying...")
                time.sleep(RETRY_DELAY)
                
    print(f"Failed to download {filename} after {MAX_RETRIES} attempts.")
    return False

if __name__ == "__main__":
    success = True
    for filename, url in URLS.items():
        if not download_file(filename, url):
            success = False
            
    if not success:
        print("One or more downloads failed. Exiting with error.")
        sys.exit(1)
