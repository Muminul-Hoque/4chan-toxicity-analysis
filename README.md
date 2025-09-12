# 🧠 4chan Toxicity Analysis  
**Yang Lab Screening Task – September 2025**

# *[⚠️ This README is a work in progress. Final documentation will be updated before submission.]*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Git](https://img.shields.io/badge/Version%20Control-Git-orange?logo=git)
![OpenAI API](https://img.shields.io/badge/API-OpenAI-green?logo=openai)
![Google Perspective API](https://img.shields.io/badge/API-Google%20Perspective-lightgrey?logo=google)
![License](https://img.shields.io/badge/License-MIT-success)
 

This repository contains a complete pipeline for analyzing toxicity patterns on 4chan’s politically incorrect board (/pol/) using two automated content moderation systems: **OpenAI’s Moderation API** and **Google’s Perspective API**.  

The project demonstrates proficiency in **ethical social media data collection, API integration, statistical analysis, version control, and technical reporting** — core competencies for research in the Yang Lab.  

---

## 📁 Repository Structure
```
4chan-toxicity-analysis/
├── 4chan_toxicity_research_report_Muhamed_Muminul_Hoque.pdf
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── pol_posts_raw.json
│   ├── pol_posts.json
│   └── pol_posts_with_scores.json
│
├── src/
│   └── main.py
|   └── data_collection.py           
|   └── processing.py                
|   └── api_integration.py
│   └── analysis.py        
│
├── results/                          # Visual outputs from analysis
│   ├── correlation_heatmap.png
│   ├── agreement_matrix.png
│   ├── toxicity_distributions.png
│   ├── openai_toxicity_distribution.png
│   ├── openai_hate_distribution.png
│   ├── openai_sexual_distribution.png
│   ├── openai_self-harm_distribution.png
│   ├── openai_violence_distribution.png
│   ├── openai_harassment_distribution.png
│   ├── openai_harassment_threatening_distribution.png
│   ├── openai_hate_threatening_distribution.png
│   ├── openai_self-harm_intent_distribution.png
│   ├── openai_sexual_minors_distribution.png
│   ├── openai_violence_graphic_distribution.png
│   ├── persp_toxicity_distribution.png
│   ├── persp_identity_attack_distribution.png
│   ├── persp_insult_distribution.png
│   ├── persp_threat_distribution.png
│   ├── persp_severe_toxicity_distribution.png
│   ├── persp_obscene_distribution.png
│   ├── persp_profanity_distribution.png
│   ├── persp_sexually_explicit_distribution.png
│   ├── persp_spam_distribution.png
│   ├── persp_flirtation_distribution.png
│
├── tables/
│   ├── disagreement_by_op.csv
│   ├── disagreement_by_country.csv
│   ├── disagreement_by_subject.csv
│   ├── disagreement_by_op.md
│   ├── disagreement_by_country.md
│   └── disagreement_by_subject.md
│
├── summary/
│   └── analysis_summary.json

```
---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/muminul-hoque/4chan-toxicity-analysis.git
cd 4chan-toxicity-analysis
```
### 2. Create a virtual environment
#### For Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
## 3. Install dependencies:
```bash
pip install -r requirements.txt
```
## 4. Configure API keys
Create a .env file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
PERSPECTIVE_API_KEY=your_google_perspective_api_key
```
## 📊 Methodology Overview

### 🔹 Data Collection
- Scraped 5,000–10,000 posts from /pol/ using 4chan’s public JSON API  
- Implemented rate limiting (1 request/sec), duplicate filtering, and metadata extraction  
- Stored structured data in JSON format for reproducibility  

### 🔹 API Integration
- Queried OpenAI Moderation API and Google Perspective API for each post  
- Extracted toxicity scores and flags across multiple categories  
- Implemented retry logic, error handling, and checkpointing for robustness  

### 🔹 Comparative Analysis
- Correlation analysis between API scores  
- Agreement/disagreement pattern identification  
- Category-wise toxicity distribution  
- Statistical significance testing  
- Visualizations using `matplotlib` and `seaborn`  

---

## 🔍 Research Questions
- How well do OpenAI and Perspective APIs agree on toxicity detection?  
- Which content categories show the highest disagreement?  
- Which API is more sensitive to specific toxic behaviors?  
- What patterns emerge in false positive/negative classifications?  

---

## 🤖 Generative AI Usage Statement
This project leveraged **Microsoft Copilot** to assist with:
- Code debugging and optimization  
- README and documentation drafting  
- Statistical analysis planning  
- Report structuring and phrasing  

All AI-generated content was reviewed, validated, and integrated manually. The use of generative AI tools was limited to support tasks and did not replace original analytical work.

---

## 🔐 Notes on Ethics and Privacy
- All data collected from 4chan was publicly accessible and gathered in accordance with platform guidelines.  
- API keys and sensitive credentials are excluded from the repository.  
- Toxicity analysis was conducted for research purposes only and does not reflect endorsement or judgment of any individual content.

---

## 📬 Contact
For questions or collaboration, please reach out via GitHub or email:  
**yang3kc@gmail.com** **muminul951@gmail.com**
