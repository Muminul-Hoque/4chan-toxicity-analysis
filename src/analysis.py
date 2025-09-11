import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, ttest_ind, chi2_contingency
from datetime import datetime

# ===== CONFIG =====
INPUT_FILE = "pol_posts_with_scores.json"
PLOT_STYLE = "whitegrid"
sns.set_theme(style=PLOT_STYLE)

# ===== LOAD DATA =====
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)

print(f"\nTotal posts analyzed: {len(df)}")


# ===== EXTRACT SCORES =====

# Perspective API attributes
persp_attributes = [
    "TOXICITY", "SEVERE_TOXICITY", "INSULT", "PROFANITY", "THREAT",
    "IDENTITY_ATTACK", "SEXUALLY_EXPLICIT", "FLIRTATION", "SPAM", "OBSCENE"
]

for attr in persp_attributes:
    df[f"persp_{attr.lower()}"] = df["perspective_scores"].apply(
        lambda x: x.get(attr, np.nan) if isinstance(x, dict) else np.nan
    )

# OpenAI Moderation API categories
openai_categories = [
    "sexual", "sexual/minors", "hate", "hate/threatening", "violence",
    "violence/graphic", "harassment", "harassment/threatening", "self-harm", "self-harm/intent"
]

for cat in openai_categories:
    df[f"openai_{cat.replace('/', '_')}"] = df["openai_moderation"].apply(
        lambda x: x.get("category_scores", {}).get(cat, np.nan) if isinstance(x, dict) else np.nan
    )

# ===== Error Handling =====
required_cols = ["openai_toxicity", "persp_toxicity"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}. Please regenerate your enriched dataset.")


# ===== 1. CORRELATION ANALYSIS =====
pearson_corr, pearson_p = pearsonr(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna())
spearman_corr, spearman_p = spearmanr(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna())

print("\n=== Correlation Analysis ===")
print(f"Pearson r: {pearson_corr:.3f} (p={pearson_p:.4f})")
print(f"Spearman rho: {spearman_corr:.3f} (p={spearman_p:.4f})")

plt.figure(figsize=(5,4))
sns.heatmap(df[["openai_toxicity", "persp_toxicity"]].corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation between OpenAI and Perspective Toxicity Scores")
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=300)
plt.close()


# ===== CATEGORY-WISE CORRELATION ANALYSIS =====
category_mapping = {
    "openai_hate": "persp_identity_attack",
    "openai_violence": "persp_threat",
    "openai_harassment": "persp_insult",
    "openai_sexual": "persp_sexually_explicit",
    "openai_self_harm": "persp_severe_toxicity",
    "openai_hate/threatening": "persp_threat"
}

correlation_results = []
for openai_col, persp_col in category_mapping.items():
    if openai_col in df.columns and persp_col in df.columns:
        o_scores = df[openai_col].dropna()
        p_scores = df[persp_col].dropna()
        if len(o_scores) > 0 and len(p_scores) > 0:
            pearson, _ = pearsonr(o_scores, p_scores)
            spearman, _ = spearmanr(o_scores, p_scores)
            correlation_results.append({
                "openai": openai_col,
                "perspective": persp_col,
                "pearson": round(pearson, 3),
                "spearman": round(spearman, 3)
            })

print("\n=== Category-Wise Correlation Analysis ===")
for result in correlation_results:
    print(f"{result['openai']} vs {result['perspective']}: "
          f"Pearson={result['pearson']}, Spearman={result['spearman']}")

# ===== DISTRIBUTIONS FOR ALL CATEGORIES =====
for col in df.columns:
    if col.startswith("openai_") or col.startswith("persp_"):
        plt.figure(figsize=(6,4))
        sns.histplot(df[col], kde=True)
        plt.title(f"{col} Score Distribution")
        plt.tight_layout()
        plt.savefig(f"{col}_distribution.png", dpi=300)
        plt.close()

# ===== 2. AGREEMENT/DISAGREEMENT =====
threshold = 0.5
df["openai_flag"] = df["openai_toxicity"] >= threshold
df["persp_flag"] = df["persp_toxicity"] >= threshold

agreement = (df["openai_flag"] == df["persp_flag"]).mean()
print(f"\nAgreement rate: {agreement*100:.2f}%")

conf_matrix = pd.crosstab(df["openai_flag"], df["persp_flag"], rownames=["OpenAI"], colnames=["Perspective"])
print("\nConfusion Matrix:\n", conf_matrix)

plt.figure(figsize=(4,3))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.title("Agreement/Disagreement Matrix")
plt.tight_layout()
plt.savefig("agreement_matrix.png", dpi=300)
plt.close()

# ===== 2B. DISAGREEMENT BY CONTENT TYPE =====
df["disagreement"] = df["openai_flag"] != df["persp_flag"]

# ===== 2A. FALSE POSITIVE / NEGATIVE ANALYSIS =====
df["false_positive"] = (df["openai_flag"] == True) & (df["persp_flag"] == False)
df["false_negative"] = (df["openai_flag"] == False) & (df["persp_flag"] == True)

false_positive_rate = df["false_positive"].mean() * 100
false_negative_rate = df["false_negative"].mean() * 100

print(f"\nFalse Positive Rate (OpenAI flagged, Perspective did not): {false_positive_rate:.2f}%")
print(f"False Negative Rate (Perspective flagged, OpenAI did not): {false_negative_rate:.2f}%")


# OP vs Reply
df["is_op"] = df["thread_id"] == df["post_id"]
op_disagree_rate = df.groupby("is_op")["disagreement"].mean() * 100

# By Country (top 10)
df["country"] = df["metadata"].apply(lambda m: m.get("country") if isinstance(m, dict) else None)
top_countries = df["country"].value_counts().head(10).index
country_disagree_rate = df[df["country"].isin(top_countries)].groupby("country")["disagreement"].mean() * 100

# By Subject (Top 5 OPs)
df["subject"] = df["metadata"].apply(lambda m: m.get("subject") if isinstance(m, dict) else None)
top_subjects = df[df["is_op"] & df["subject"].notna()]["subject"].value_counts().head(5).index
subject_disagree_rate = df[df["subject"].isin(top_subjects)].groupby("subject")["disagreement"].mean() * 100

# Save breakdowns
op_disagree_rate.to_csv("disagreement_by_op.csv")
country_disagree_rate.to_csv("disagreement_by_country.csv")
subject_disagree_rate.to_csv("disagreement_by_subject.csv")

# Also save Markdown tables for report
op_disagree_rate.to_frame("Disagreement %").to_markdown("disagreement_by_op.md")
country_disagree_rate.to_frame("Disagreement %").to_markdown("disagreement_by_country.md")
subject_disagree_rate.to_frame("Disagreement %").to_markdown("disagreement_by_subject.md")

# ===== 3. CATEGORY-WISE DISTRIBUTION =====
plt.figure(figsize=(8,5))
sns.histplot(df["persp_toxicity"], color="red", label="Perspective", kde=True)
sns.histplot(df["openai_toxicity"], color="blue", label="OpenAI", kde=True)
plt.legend()
plt.xlabel("Toxicity Score")
plt.ylabel("Frequency")
plt.title("Toxicity Score Distributions")
plt.tight_layout()
plt.savefig("toxicity_distributions.png", dpi=300)
plt.close()

# ===== 4. STATISTICAL SIGNIFICANCE TESTING =====
t_stat, t_p = ttest_ind(df["openai_toxicity"].dropna(), df["persp_toxicity"].dropna(), equal_var=False)
chi2, chi_p, _, _ = chi2_contingency(conf_matrix)

print(f"\nT-test: t={t_stat:.3f}, p={t_p:.4f}")
print(f"Chi-square: χ²={chi2:.3f}, p={chi_p:.4f}")



# ===== 5. SAVE SUMMARY =====
summary = {
    "pearson_corr": pearson_corr,
    "pearson_p": pearson_p,
    "spearman_corr": spearman_corr,
    "spearman_p": spearman_p,
    "agreement_rate": agreement,
    "false_positive_rate": false_positive_rate,
    "false_negative_rate": false_negative_rate,
    "t_test": {"t_stat": t_stat, "p_value": t_p},
    "chi_square": {"chi2": chi2, "p_value": chi_p},
    "op_disagreement_rate": op_disagree_rate.to_dict(),
    "country_disagreement_rate": country_disagree_rate.to_dict(),
    "subject_disagreement_rate": subject_disagree_rate.to_dict()
}

summary["category_correlations"] = correlation_results

summary["generated_at"] = datetime.utcnow().isoformat() + "Z"


with open("analysis_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\n✅ Analysis complete. Plots saved as PNG, CSV + Markdown tables saved, summary saved to analysis_summary.json")
