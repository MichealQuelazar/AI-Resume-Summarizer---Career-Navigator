# Career Navigator 🚀

A hackathon-built prototype that helps users explore career
opportunities by analyzing resumes, job postings, and skill gaps.

## ✨ Features

-   **Resume Summarization**: Uses **Gemini API + RAG** to extract key
    skills and achievements.\
-   **Career Path Recommendations**: Suggests potential roles based on
    extracted resume insights.\
-   **Job Market Analysis**:
    -   Integrated with **Apify API** to fetch live LinkedIn job
        postings.\
    -   Dataset of **2,500+ jobs** analyzed for salary trends and demand
        insights.\
-   **Interactive Dashboard**: Built with **Streamlit** to display:
    -   Skill-gap analysis\
    -   Bar charts for salary distribution\
    -   Job availability insights

## ⚙️ Tech Stack

-   **Backend**: Python, Gemini API, RAG\
-   **Data**: Apify API (LinkedIn job scraping), Pandas\
-   **Frontend**: Streamlit (dashboard & visualizations)\
-   **Visualization**: Matplotlib / Plotly

## 🚀 Quick Start

```bash \# Clone the repo git clone
https://github.com/your-username/career-navigator.git cd
career-navigator
```

## Install dependencies
```bash
pip install -r requirements.txt
```
```bash
# Run the app
streamlit run app.py
```

## 🎥 Demo Video    
[Demo pt1](https://drive.google.com/file/d/1SAXS_lVL5ijFA62GNP3oJ0D8h6NzldO2/view?usp=sharing) 
[Demo pt2](https://drive.google.com/file/d/1SAXS_lVL5ijFA62GNP3oJ0D8h6NzldO2/view?usp=sharing) 


## 🏆 Hackathon Context

-   Built in **2 hours** during a hackathon.\
-   Focused on **AI + career guidance + real-time job data**.

## 📌 Future Enhancements

-   Add support for multiple resume formats (PDF/DOCX parsing).\
-   Expand data sources beyond LinkedIn.\
-   Personalized learning resources for identified skill gaps.
