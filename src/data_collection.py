import requests
import time
import json
import os
from datetime import datetime

# ===== CONFIGURATION =====
BOARD = "pol"  # 4chan board to scrape
OUTPUT_FILE = f"{BOARD}_posts_raw.json"  # raw data file
RATE_LIMIT_SECONDS = 1
MAX_POSTS = 10000  # Stop after collecting this many posts

# ===== DUPLICATE TRACKING =====
seen_posts = set()
collected_data = []

# ===== LOAD EXISTING DATA (resume capability) =====
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        try:
            collected_data = json.load(f)
            seen_posts = {post["post_id"] for post in collected_data}
            print(f"Loaded {len(collected_data)} existing posts from {OUTPUT_FILE}")
        except json.JSONDecodeError:
            print("Warning: Could not parse existing JSON file. Starting fresh.")

# ===== FETCH CATALOG =====
def fetch_catalog():
    url = f"https://a.4cdn.org/{BOARD}/catalog.json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch catalog: {e}")
        return []

# ===== FETCH THREAD =====
def fetch_thread(thread_id):
    url = f"https://a.4cdn.org/{BOARD}/thread/{thread_id}.json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch thread {thread_id}: {e}")
        return None

# ===== MAIN COLLECTION =====
def collect_posts():
    total_collected = len(collected_data)
    catalog = fetch_catalog()

    for page in catalog:
        for thread in page.get("threads", []):
            thread_id = thread.get("no")
            thread_data = fetch_thread(thread_id)
            time.sleep(RATE_LIMIT_SECONDS)  # Respect rate limit

            if not thread_data:
                continue

            for post in thread_data.get("posts", []):
                # ✅ Check limit BEFORE adding anything
                if total_collected >= MAX_POSTS:
                    print(f"Reached {MAX_POSTS} posts. Stopping collection.")
                    return

                post_id = post.get("no")
                if post_id in seen_posts:
                    continue  # Skip duplicates

                # Build structured post entry (raw HTML only)
                post_entry = {
                    "post_id": post_id,
                    "thread_id": thread_id,
                    "timestamp": post.get("time"),
                    "datetime_utc": datetime.utcfromtimestamp(post.get("time")).isoformat() if post.get("time") else None,
                    "comment_html": post.get("com", ""),  # raw HTML only
                    "metadata": {
                        "name": post.get("name"),
                        "trip": post.get("trip"),
                        "poster_id": post.get("id"),
                        "country": post.get("country"),
                        "country_name": post.get("country_name"),
                        "subject": post.get("sub"),
                        "replies": post.get("replies"),
                        "images": post.get("images")
                    }
                }

                collected_data.append(post_entry)
                seen_posts.add(post_id)
                total_collected += 1

                if total_collected % 100 == 0:
                    print(f"Collected {total_collected} posts so far...")


# ===== SAVE FUNCTION =====
def save_data():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(collected_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(collected_data)} raw posts to {OUTPUT_FILE}")

# ===== RUN ONLY IF EXECUTED DIRECTLY =====
if __name__ == "__main__":
    collect_posts()
    save_data()
