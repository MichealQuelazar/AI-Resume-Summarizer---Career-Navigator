<div align="center">
    <img width="480" height="101" alt="image" src="https://github.com/user-attachments/assets/7c762de8-c458-40fb-be7a-b3bd0d3989ce" />
 </div>

<div align="center">
  <h1>AI-Resume-Summarizer — Career Navigator </h1>
  <p>
    <img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" alt="Open Source">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat" alt="PRs Welcome">
    <img src="https://api.visitorbadge.io/api/Visitors?path=MichealQuelazar%2FAI-Resume-Summarizer---Career-Navigator&countColor=%23263759&style=flat" alt="Visitors">
    <img src="https://img.shields.io/github/forks/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Forks">
    <img src="https://img.shields.io/github/stars/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Stars">
    <img src="https://img.shields.io/github/contributors/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Contributors">
    <img src="https://img.shields.io/github/last-commit/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Last Commit">
    <img src="https://img.shields.io/github/repo-size/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Repo Size">
    <img src="https://img.shields.io/github/license/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="License">
    <img src="https://img.shields.io/github/issues/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Open Issues">
    <img src="https://img.shields.io/github/issues-closed-raw/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Closed Issues">
    <img src="https://img.shields.io/github/issues-pr/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="PRs">
    <img src="https://img.shields.io/github/issues-pr-closed/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator" alt="Closed PRs">
  </p>
</div>
 
  Live Demo
AI-Resume-Summarizer — Career Navigato live here: 👉 [![**>AI-Resume-Summarizer — Career Navigator**](https://img.shields.io/badge/View-Live%20Demo-blue?style=for-the-badge)](https://ai-resume-summarizer---career-navigator-app.streamlit.app/)

The AI Resume Summarizer and Career Navigator is a fully deployed AI-powered web application that helps users explore personalized career opportunities by analyzing their resumes, identifying skill gaps, and matching them with real-time job market data.
Unlike early prototypes, the current system is a production-ready solution, deployed on Streamlit Cloud with complete integration of APIs and visual dashboards.


## 🌍 Vision
AI-Resume-Summarizer — Career Navigator helps professionals and students transform static resumes into *actionable insights*.  
It summarizes lengthy CVs, identifies core strengths, and recommends personalized career directions — powered by **Groq API’s ultra-fast inference** and modern NLP.

> ✨ *“From résumé clutter to clarity — your career, simplified by AI.”*

---

## 💡 Why It Matters
Most job seekers struggle with tailoring their resumes and understanding what recruiters see.  
This tool bridges that gap — turning raw data into guidance, summaries, and skill-based insights — within seconds.

---

##   Features

##  Features Overview

###  AI Resume Summarization
* **Groq-powered summarization engine**: Uses **Groq API** to analyze resumes and generate concise, recruiter-friendly summaries in seconds.  
* **Contextual understanding**: Detects achievements, project relevance, and key experience areas rather than just keywords.  
* **Multi-format support**: Upload PDF or DOCX — the app automatically extracts and preprocesses text.  

<div align="center">
  <img width="1512" height="842" alt="image" src="https://github.com/user-attachments/assets/b0b256ce-fda0-4137-9a3e-c0fd26b5b2d3" />

  <br>
</div>

---

###  Skill & Domain Extraction
* **Intelligent Skill Parser**: Extracts both technical and soft skills, mapping them to industry-standard categories.  
* **Ranking by relevance**: Highlights the most important skills based on job market trends.  
  

<div align="center">
  <img width="1504" height="875" alt="Screenshot 2025-09-28 145445" src="https://github.com/user-attachments/assets/280b9c62-4e81-45f2-ae15-1bb9a50a1202" />
  <br>
</div>

---

###  Career Path Suggestions
* **AI-driven recommendation engine**: Suggests tailored career paths and roles aligned with your strengths.  
* **Job-fit analysis**: Evaluates resume content against trending positions in your dataset.  
* **Growth insights**: Identifies learning areas and skill gaps for future roles.  

<div align="center">
<img width="1918" height="922" alt="image" src="https://github.com/user-attachments/assets/c2e46110-eb07-4edf-b2d7-f9d03916750c" />

  <br>
</div>

---

### 🗣️ AI Career Chatbot
* **Groq + Gemini-powered dialogue**: An intelligent chatbot built using **Groq API** for ultra-fast inference and **Gemini 2.0** for natural conversation.  
* **Personalized advice**: Users can ask questions like _“What skills should I learn for Data Science?”_ or _“Which roles fit a marketing background?”_.  

<div align="center">
 <img width="1918" height="905" alt="image" src="https://github.com/user-attachments/assets/08c83061-40ba-4624-b01f-64a120e7d029" />

  <br>
</div>


###  Insights Dashboard
* **Visual job analytics based on resume**: Graphical breakdown of career matches.  

<div align="center">
  <img width="1404" height="635" alt="image" src="https://github.com/user-attachments/assets/3f2ff9b6-9043-474b-b387-c58e98509089" />
  <br>
</div>

---

##  Tech Stack

-   **Backend**: Python, GROQ API, RAG
-   **Data**: Apify API (LinkedIn job scraping), Pandas
-   **Frontend**: Streamlit (dashboard & visualizations)
-   **Visualization**: Matplotlib / Plotly

## 📁 Project Structure

<details>
<summary><strong>🗂️ Click to view detailed project architecture</strong></summary>

```bash
AI-Resume-Summarizer---Career-Navigator/
├── chroma_db/                   # Chroma vector store for RAG
├── data/                        # Sample resumes and job data
├── pitch and demo/              # Demo scripts and presentation materials
├── src/                         # Core application code
│   ├── app.py                   # Main Streamlit app entry point
│   ├── config.py                # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   └── setup.py                 # Setup script
├── .gitignore                   # Git ignore file
└── LICENSE                      # Project license


```
</details> ```
    
## 🚀 Quick Start

```bash \# Clone the repo git clone
https://github.com/MichealQuelazar/AI-Resume-Summarizer---Career-Navigator.git
```

## Install dependencies
```bash
pip install -r requirements.txt
```
## Run the app
```bash
streamlit run app.py
```


##  Demo(pt1 and 2)
[<img width="640" alt="Demo Part 1" src="https://github.com/user-attachments/assets/ff4c1239-5e1e-4e1d-99f5-0b8e16ad716e" />](https://drive.google.com/file/d/1SAXS_lVL5ijFA62GNP3oJ0D8h6NzldO2/preview)


[<img width="640" alt="Demo Part 2" src="https://github.com/user-attachments/assets/0404c056-72b9-4b06-be7e-a709d4a3df1b" />](https://drive.google.com/file/d/1vK4c-dGYzBcvGn9NHiXwnMN0LAUpuThE/preview)


-   Now deployed on Streamlit cloud

## 📌 Future Enhancements

-   Add support for multiple resume formats (PDF/DOCX parsing).\
-   Expand data sources beyond LinkedIn.\
-   Personalized learning resources for identified skill gaps.
