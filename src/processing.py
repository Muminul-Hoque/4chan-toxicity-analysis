import json
import os
from bs4 import BeautifulSoup
import html as htmllib

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RAW_FILE = os.path.join(DATA_DIR, "pol_posts_raw.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "pol_posts.json")

# ===== CLEANING FUNCTION =====
def clean_comment(html_text: str) -> str:
    if not html_text:
        return ""
    text = BeautifulSoup(html_text, "html.parser").get_text(separator=" ")
    text = htmllib.unescape(text)
    return " ".join(text.split())

# ===== MAIN PROCESSING =====
def process_posts():
    if not os.path.exists(RAW_FILE):
        print(f"[ERROR] Raw file {RAW_FILE} not found.")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Clean comment text
    for post in posts:
        post["comment_text"] = clean_comment(post.get("comment_html", ""))

    # Filter out short/empty comments
    before = len(posts)
    posts = [post for post in posts if len(post["comment_text"]) > 10]
    after = len(posts)
    print(f"Filtered out {before - after} short/empty comments. {after} posts retained.")

    # Save processed data
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ Processed {after} posts and saved to {PROCESSED_FILE}")

# ===== RUN ONLY IF EXECUTED DIRECTLY =====
if __name__ == "__main__":
    process_posts()
