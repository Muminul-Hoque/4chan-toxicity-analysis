import os
import json
import argparse
import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, ttest_rel, chi2_contingency
from datetime import datetime
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

# ===== CONFIG =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TABLES_DIR = os.path.join(BASE_DIR, "tables")
SUMMARY_DIR = os.path.join(BASE_DIR, "summary")

INPUT_FILE = os.path.join(DATA_DIR, "pol_posts_with_scores.json")

# Ensure output folders exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")

# ===== LOGGING CONFIG =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(SUMMARY_DIR, "analysis.log"), mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ===== ARGPARSE =====
parser = argparse.ArgumentParser(description="4chan Toxicity Analysis")
parser.add_argument("--fast", action="store_true",
                    help="Skip heavy plots (distributions/heatmaps) for faster runs.")
args = parser.parse_args()

# ===== LOAD DATA =====
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)
logger.info(f"Total posts analyzed: {len(df)}")

# ===== EXTRACT SCORES =====
persp_attributes = [
    "TOXICITY", "SEVERE_TOXICITY", "INSULT", "PROFANITY", "THREAT",
    "IDENTITY_ATTACK", "SEXUALLY_EXPLICIT", "FLIRTATION", "SPAM", "OBSCENE"
]
for attr in persp_attributes:
    df[f"persp_{attr.lower()}"] = df["perspective_scores"].apply(
        lambda x: x.get(attr, np.nan) if isinstance(x, dict) else np.nan
    )

openai_categories = [
    "sexual", "sexual/minors", "hate", "hate/threatening", "violence",
    "violence/graphic", "harassment", "harassment/threatening",
    "self-harm", "self-harm/intent"
]
for cat in openai_categories:
    df[f"openai_{cat.replace('/', '_')}"] = df["openai_moderation"].apply(
        lambda x: x.get("category_scores", {}).get(cat, np.nan) if isinstance(x, dict) else np.nan
    )

# Ensure required columns exist
required_cols = ["openai_toxicity", "persp_toxicity"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    logger.error(f"Missing required columns: {missing}. Please regenerate dataset.")
    raise ValueError(f"Missing required columns: {missing}")

# ===== CORRELATION ANALYSIS =====
pearson_corr, pearson_p = pearsonr(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna())
spearman_corr, spearman_p = spearmanr(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna())
logger.info(f"Pearson corr = {pearson_corr:.3f} (p={pearson_p:.4f})")
logger.info(f"Spearman corr = {spearman_corr:.3f} (p={spearman_p:.4f})")

def fisher_ci(r, n, alpha=0.05):
    if abs(r) == 1 or n <= 3:
        return (np.nan, np.nan)
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    z_crit = 1.96
    lo, hi = z - z_crit * se, z + z_crit * se
    return np.tanh(lo), np.tanh(hi)

pearson_ci = fisher_ci(pearson_corr, len(df.dropna(subset=["openai_toxicity", "persp_toxicity"])))
logger.info(f"Pearson 95% CI: {pearson_ci}")

if not args.fast:
    plt.figure(figsize=(5, 4))
    sns.heatmap(df[["openai_toxicity", "persp_toxicity"]].corr(), annot=True,
                cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation between OpenAI and Perspective Toxicity Scores")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "correlation_heatmap.png"), dpi=300)
    plt.close()
    logger.info("Saved correlation_heatmap.png")

# ===== CATEGORY-WISE CORRELATION =====
category_mapping = {
    "openai_hate": "persp_identity_attack",
    "openai_violence": "persp_threat",
    "openai_harassment": "persp_insult",
    "openai_sexual": "persp_sexually_explicit",
    "openai_hate_threatening": "persp_threat",
}
correlation_results = []
for openai_col, persp_col in category_mapping.items():
    if openai_col in df.columns and persp_col in df.columns:
        subset = df[[openai_col, persp_col]].dropna()
        if len(subset) >= 2:
            pr, _ = pearsonr(subset[openai_col], subset[persp_col])
            sr, _ = spearmanr(subset[openai_col], subset[persp_col])
            correlation_results.append({
                "openai": openai_col,
                "perspective": persp_col,
                "pearson": round(pr, 3),
                "spearman": round(sr, 3),
            })
logger.info(f"Category correlations computed for {len(correlation_results)} mappings")

# ===== DISTRIBUTIONS =====
if not args.fast:
    for col in df.columns:
        if col.startswith("openai_") or col.startswith("persp_"):
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) == 0:
                continue
            plt.figure(figsize=(6, 4))
            sns.histplot(series, kde=(len(series) >= 2), color="#4C72B0", edgecolor="black")
            plt.axvline(series.mean(), color="red", linestyle="--", linewidth=1.2,
                        label=f"Mean: {series.mean():.2f}")
            plt.axvline(series.median(), color="green", linestyle=":",
                        linewidth=1.2, label=f"Median: {series.median():.2f}")
            plt.title(f"{col.replace('_', ' ').title()} Distribution", fontsize=14, weight="bold")
            plt.xlabel("Score")
            plt.ylabel("Frequency")
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(RESULTS_DIR, f"{col}_distribution.png"), dpi=300)
            plt.close()
    logger.info("Saved all distributions")
    
    # Combined toxicity score distribution
    plt.figure(figsize=(6, 4))
    sns.histplot(df["openai_toxicity"], kde=True, color="#4C72B0", edgecolor="black", label="OpenAI", alpha=0.5)
    sns.histplot(df["persp_toxicity"], kde=True, color="#E24A33", edgecolor="black", label="Perspective", alpha=0.5)
    plt.axvline(df["openai_toxicity"].mean(), color="#4C72B0", linestyle="--", linewidth=1.2,
                label=f"OpenAI Mean: {df['openai_toxicity'].mean():.2f}")
    plt.axvline(df["persp_toxicity"].mean(), color="#E24A33", linestyle="--", linewidth=1.2,
                label=f"Perspective Mean: {df['persp_toxicity'].mean():.2f}")
    plt.title("Toxicity Score Distributions", fontsize=14, weight="bold")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "toxicity_distributions.png"), dpi=300)
    plt.close()
    logger.info("Saved toxicity_distributions.png")

# ===== AGREEMENT/DISAGREEMENT =====
threshold = 0.5
df["openai_flag"] = df["openai_toxicity"] >= threshold
df["persp_flag"] = df["persp_toxicity"] >= threshold

# True if APIs disagree on this post
df["disagreement"] = df["openai_flag"] != df["persp_flag"]

conf_matrix = pd.crosstab(df["openai_flag"], df["persp_flag"])
plt.figure(figsize=(4, 3))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.title("Agreement/Disagreement Matrix")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "agreement_matrix.png"), dpi=300)
plt.close()
logger.info("Saved agreement_matrix.png")

cm = confusion_matrix(df["persp_flag"], df["openai_flag"], labels=[False, True])
cm_df = pd.DataFrame(cm,
                     index=["Perspective: Non-toxic", "Perspective: Toxic"],
                     columns=["OpenAI: Non-toxic", "OpenAI: Toxic"])
cm_df.to_csv(os.path.join(TABLES_DIR, "confusion_matrix.csv"))
cm_df.to_markdown(os.path.join(TABLES_DIR, "confusion_matrix.md"))
logger.info("Saved confusion matrix tables")

precision, recall, f1, support = precision_recall_fscore_support(
    df["persp_flag"], df["openai_flag"], average=None, labels=[False, True]
)
metrics_df = pd.DataFrame({
    "Class": ["Non-toxic", "Toxic"],
    "Precision": precision,
    "Recall": recall,
    "F1-score": f1,
    "Support": support
})
metrics_df.to_csv(os.path.join(TABLES_DIR, "precision_recall_table.csv"), index=False)
metrics_df.to_markdown(os.path.join(TABLES_DIR, "precision_recall_table.md"), index=False)
logger.info("Saved precision/recall tables")

# Breakdown: OP vs reply
df["is_op"] = df["thread_id"] == df["post_id"]
op_disagree_rate = df.groupby("is_op")["disagreement"].mean() * 100

op_disagree_rate.to_csv(os.path.join(TABLES_DIR, "disagreement_by_op.csv"))
op_disagree_rate.to_frame("Disagreement %").to_markdown(os.path.join(TABLES_DIR, "disagreement_by_op.md"))
logger.info("Saved OP vs reply disagreement")

# Breakdown: by country
df["country"] = df["metadata"].apply(lambda m: m.get("country") if isinstance(m, dict) else None)
country_counts = df["country"].value_counts()
valid_countries = country_counts[country_counts >= 25].index
country_disagree = (
    df[df["country"].isin(valid_countries)]
    .groupby("country")["disagreement"].mean()
    .sort_values(ascending=False) * 100
)

country_disagree.to_csv(os.path.join(TABLES_DIR, "disagreement_by_country.csv"))
country_disagree.to_frame("Disagreement %").to_markdown(os.path.join(TABLES_DIR, "disagreement_by_country.md"))
logger.info("Saved country disagreement")

# ===== STATS & SUMMARY =====
t_stat, t_p = ttest_rel(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna())
diff = df["openai_toxicity"].dropna() - df["persp_toxicity"].dropna()
cohens_d = diff.mean() / diff.std(ddof=1)
chi2, chi_p, _, _ = chi2_contingency(conf_matrix)

summary = {
    "pearson_corr": pearson_corr,
    "pearson_r_ci": pearson_ci,   
    "spearman_corr": spearman_corr,
    "spearman_p": spearman_p,
    "agreement_rate": (df["openai_flag"] == df["persp_flag"]).mean(),
    "false_positive_rate": (df["openai_flag"] & ~df["persp_flag"]).mean() * 100,
    "false_negative_rate": (~df["openai_flag"] & df["persp_flag"]).mean() * 100,
    "t_test": {"t_stat": t_stat, "p_value": t_p},
    "cohen_d": cohens_d,          
    "chi_square": {"chi2": chi2, "p_value": chi_p},
    "op_disagreement_rate": op_disagree_rate.to_dict(),
    "country_disagreement_rate": country_disagree.to_dict(),
    "category_correlations": correlation_results,
    "generated_at": datetime.utcnow().isoformat() + "Z"
}


with open(os.path.join(SUMMARY_DIR, "analysis_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
logger.info("Saved analysis_summary.json")

logger.info("✅ Analysis complete. Results saved into /results, /tables, and /summary")
