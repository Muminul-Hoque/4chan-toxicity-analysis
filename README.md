# 🧠 4chan Toxicity Analysis  
**Yang Lab Screening Task – September 2025**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Git](https://img.shields.io/badge/Version%20Control-Git-orange?logo=git)
![OpenAI API](https://img.shields.io/badge/API-OpenAI-green?logo=openai)
![Google Perspective API](https://img.shields.io/badge/API-Google%20Perspective-lightgrey?logo=google)
![License](https://img.shields.io/badge/License-MIT-success)
 

This repository contains a complete pipeline for analyzing toxicity patterns on 4chan’s politically incorrect board (/pol/) using two automated content moderation systems: **OpenAI’s Moderation API** and **Google’s Perspective API**.  

The project demonstrates proficiency in **ethical social media data collection, API integration, statistical analysis, version control, and technical reporting** — core competencies for research in the Yang Lab.  

---

## 📁 Repository Structure
├── data_collection.py           # Scrapes raw posts from /pol/ using 4chan’s JSON API
├── processing.py                # Cleans and structures raw post data
├── api_integration.py           # Enriches posts with toxicity scores from OpenAI & Perspective APIs
├── analysis.ipynb               # Statistical comparison and visualization of toxicity scores
├── pol_posts.json               # Cleaned post data (OPs and replies)
├── pol_posts_with_scores.json   # Posts enriched with API scores
├── report.pdf                   # Final research report
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation


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
