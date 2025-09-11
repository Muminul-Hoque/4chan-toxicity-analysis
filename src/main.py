import subprocess

# Helper to run each stage and stop if it fails
def run_stage(description, command):
    print(f"\n=== {description} ===")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"[ERROR] {description} failed. Stopping pipeline.")
        exit(1)

if __name__ == "__main__":
    # 1. Data Collection
    run_stage("Data Collection", "python data_collection.py")

    # 2. Processing
    run_stage("Processing", "python processing.py")

    # 3. API Integration
    run_stage("API Integration", "python api_integration.py")

    # 4. Analysis
    run_stage("Analysis", "python analysis.py")

    print("\n✅ Pipeline complete! Check output files and plots in your project folder.")
