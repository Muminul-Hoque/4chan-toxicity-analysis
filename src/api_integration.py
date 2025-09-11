from dotenv import load_dotenv
import os, json, time, requests, random
from openai import OpenAI

# ===== CONFIGURATION =====
INPUT_FILE = "pol_posts.json"   # from processing.py
OUTPUT_FILE = "pol_posts_with_scores.json"

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== OPENAI MODERATION API =====
def get_openai_moderation(text):
    if not text.strip():
        return None
    try:
        response = client.moderations.create(
            model="text-moderation-latest",
            input=text
        )
        return response.model_dump()["results"][0]  
    except Exception as e:
        print(f"[ERROR] OpenAI Moderation failed: {e}")
        return None


# ===== GOOGLE PERSPECTIVE API =====
def get_perspective_scores(text):
    if not text.strip():
        return None
    try:
        url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={PERSPECTIVE_API_KEY}"
        body = {
            "comment": {"text": text},
            "languages": ["en"],
            "requestedAttributes": {
                "TOXICITY": {}, "SEVERE_TOXICITY": {}, "INSULT": {}, "PROFANITY": {}, "THREAT": {},"IDENTITY_ATTACK": {}, "SEXUALLY_EXPLICIT": {}, "FLIRTATION": {}, "SPAM": {}, "OBSCENE": {}
                }
        }
        r = requests.post(url, json=body, timeout=10)
        r.raise_for_status()
        scores = {}
        for attr, val in r.json().get("attributeScores", {}).items():
            scores[attr] = val["summaryScore"]["value"]
        return scores
    except Exception as e:
        print(f"[ERROR] Perspective API failed: {e}")
        return None

# ===== Retry wrapper =====
def safe_call(func, *args, retries=3):
    for i in range(retries):
        try:
            return func(*args)
        except Exception as e:
            print(f"[WARN] {func.__name__} failed (attempt {i+1}): {e}")
            time.sleep((2 ** i) + random.random())
    return None



# ===== Internet Connectivity Check =====
def is_connected():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

# ===== MAIN INTEGRATION =====
def run_api_analysis():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    enriched_posts = []
    processed_ids = set()
    missing_count = 0

    # Resume from previous output if available
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                enriched_posts = json.load(f)
                processed_ids = {post.get("post_id") for post in enriched_posts if post.get("post_id")}
                print(f"🔄 Resuming from {len(enriched_posts)} posts")
            except json.JSONDecodeError:
                print("⚠️ Could not parse existing output file. Starting fresh.")

    try:
        for idx, post in enumerate(posts, start=1):
            post_id = post.get("post_id") or idx
            if post_id in processed_ids:
                continue

            text = post.get("comment_text", "")

            if idx <= 3:
                print(f"\n--- Post {idx} sample input ---")
                print(text)
                print("------------------------------")

            # Check internet before OpenAI call
            while not is_connected():
                print("🌐 No internet connection. Retrying in 10 seconds...")
                time.sleep(10)

            openai_result = safe_call(get_openai_moderation, text)
            time.sleep(1)

            # ✅ Correct OpenAI toxicity extraction
            openai_scores = openai_result.get("category_scores", {}) if openai_result else {}
            openai_toxicity = sum([
                openai_scores.get("hate", 0),
                openai_scores.get("harassment", 0),
                openai_scores.get("violence", 0),
                openai_scores.get("sexual", 0),
                openai_scores.get("self-harm", 0)
                ])


            # Check internet before Perspective call
            while not is_connected():
                print("🌐 No internet connection. Retrying in 10 seconds...")
                time.sleep(10)

            perspective_result = safe_call(get_perspective_scores, text)
            time.sleep(1)

            # ✅ Perspective toxicity extraction
            persp_toxicity = perspective_result.get("TOXICITY") if perspective_result else None
            
            # 🔍 Debug print for first few posts
            if idx <= 3:
                print(f"\n🔍 OpenAI response for post {post_id}:\n", json.dumps(openai_result, indent=2))
                print(f"\n🔍 Perspective response for post {post_id}:\n", json.dumps(perspective_result, indent=2))
                
            # ✅ Count and warn if scores are missing
            if openai_toxicity is None or persp_toxicity is None:
                print(f"[WARN] Missing toxicity scores for post {post_id}")
                missing_count += 1

            # ✅ Enrich post with fallback values
            post["openai_moderation"] = openai_result
            post["openai_toxicity"] = openai_toxicity if openai_toxicity is not None else None
            post["perspective_scores"] = perspective_result
            post["persp_toxicity"] = persp_toxicity if persp_toxicity is not None else None
            post["post_id"] = post_id
            enriched_posts.append(post)

            if idx % 50 == 0:
                print(f"Processed {idx}/{len(posts)} posts...")

            if idx % 100 == 0:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(enriched_posts, f, ensure_ascii=False, indent=2)
                print(f"💾 Saved checkpoint at {idx} posts")

    finally:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(enriched_posts, f, ensure_ascii=False, indent=2)
        print(f"✅ Final save completed with {len(enriched_posts)} posts")
        print(f"⚠️ Total posts missing toxicity scores: {missing_count}")

if __name__ == "__main__":
    run_api_analysis()

