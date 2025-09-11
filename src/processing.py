import json
import os
from bs4 import BeautifulSoup
import html as htmllib

RAW_FILE = "pol_posts_raw.json"
PROCESSED_FILE = "pol_posts.json"

def clean_comment(html_text: str) -> str:
    if not html_text:
        return ""
    text = BeautifulSoup(html_text, "html.parser").get_text(separator=" ")
    text = htmllib.unescape(text)
    return " ".join(text.split())

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

if __name__ == "__main__":
    process_posts()
