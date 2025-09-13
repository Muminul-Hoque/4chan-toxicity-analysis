import subprocess
import sys
import os

# === PATH SETUP ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure output directories exist
for folder in ["results", "tables", "summary"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# Helper to run each stage and stop if it fails
def run_stage(description, script_name):
    script_path = os.path.join(SRC_DIR, script_name)
    print(f"\n=== {description} ===")
    result = subprocess.run([sys.executable, script_path], cwd=SRC_DIR)
    if result.returncode != 0:
        print(f"[ERROR] {description} failed. Stopping pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Data Collection
    run_stage("Data Collection", "data_collection.py")

    # 2. Processing
    run_stage("Processing", "processing.py")

    # 3. API Integration
    run_stage("API Integration", "api_integration.py")

    # 4. Analysis
    run_stage("Analysis", "analysis.py")

    print("\n✅ Pipeline complete! Check outputs in:")
    print(f"   - Data:     {DATA_DIR}")
    print(f"   - Results:  {os.path.join(BASE_DIR, 'results')}")
    print(f"   - Tables:   {os.path.join(BASE_DIR, 'tables')}")
    print(f"   - Summary:  {os.path.join(BASE_DIR, 'summary')}")

