import streamlit as st
import re
from src.helper import extract_text_from_pdf, ask_gemini
from src.job_api import fetch_linkedin_jobs
from src.rag_engine import RAGEngine
from src.career_analytics import CareerAnalytics

# Page configuration
st.set_page_config(
    page_title="AI Resume Summarizer & Career Navigator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'analytics_engine' not in st.session_state:
    st.session_state.analytics_engine = None



# Sidebar navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["📄 Resume Analysis", "💬 Career Chat", "📊 Market Analytics", "🔍 Job Search"]
)

# Main title
st.title("🤖 AI Resume Summarizer & Career Navigator")
st.markdown("*Your intelligent career companion powered by RAG technology*")

# Initialize engines
@st.cache_resource
def initialize_engines():
    rag_engine = RAGEngine()
    analytics_engine = CareerAnalytics()
    return rag_engine, analytics_engine

if st.session_state.rag_engine is None:
    with st.spinner("Initializing AI engines..."):
        st.session_state.rag_engine, st.session_state.analytics_engine = initialize_engines()

# Resume upload section (always visible)
with st.container():
    st.subheader("📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file and st.session_state.resume_text is None:
        with st.spinner("Processing your resume..."):
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
        st.success("✅ Resume processed successfully!")

# Page content based on selection
if page == "📄 Resume Analysis":
    if st.session_state.resume_text:
        st.header("📑 Comprehensive Resume Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("Analyzing your resume..."):
                summary = ask_gemini(
                    f"Provide a comprehensive summary of this resume highlighting skills, education, experience, and strengths: \n\n{st.session_state.resume_text}", 
                    max_tokens=600
                )
            
            st.subheader("📋 Resume Summary")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {summary}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            with st.spinner("Identifying skill gaps..."):
                gaps = ask_gemini(
                    f"Analyze this resume and identify specific skill gaps, missing certifications, and areas for improvement based on current market demands: \n\n{st.session_state.resume_text}", 
                    max_tokens=500
                )
            
            st.subheader("🎯 Skill Gap Analysis")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
                {gaps}
            </div>
            """, unsafe_allow_html=True)
        
        # Career roadmap
        with st.spinner("Creating personalized roadmap..."):
            roadmap = ask_gemini(
                f"Create a detailed 6-month and 1-year career roadmap for this person including specific skills to learn, certifications to pursue, and career moves to consider: \n\n{st.session_state.resume_text}", 
                max_tokens=600
            )
        
        st.subheader("🚀 Personalized Career Roadmap")
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 15px; color: white; margin: 10px 0;'>
            {roadmap}
        </div>
        """, unsafe_allow_html=True)
        
        # RAG-based insights
        if st.button("🔍 Get AI-Powered Career Insights", type="primary"):
            with st.spinner("Analyzing job market data..."):
                insights = st.session_state.rag_engine.get_career_insights(st.session_state.resume_text)
            
            st.subheader("🎯 Market-Based Career Insights")
            st.markdown(insights['insights'])
            
            st.subheader("💼 Relevant Job Opportunities")
            for i, job in enumerate(insights['relevant_jobs'][:5]):
                with st.expander(f"🏢 {job['job_title']} - {job['industry']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Skills Required:** {job['skills'][:200]}...")
                        st.write(f"**Experience:** {job['experience']}")
                    with col2:
                        st.write(f"**Industry:** {job['industry']}")
                        st.write(f"**Salary:** {job['salary']}")
                        st.progress(job['relevance_score'])
                        st.caption(f"Relevance: {job['relevance_score']:.2%}")
    
    else:
        st.info("👆 Please upload your resume to start the analysis")

elif page == "💬 Career Chat":
    st.header("💬 Chat with Your AI Career Advisor")
    
    if st.session_state.resume_text:
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your career..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.rag_engine.chat_with_career_advisor(
                        st.session_state.resume_text,
                        st.session_state.chat_history,
                        prompt
                    )
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Quick action buttons
        st.subheader("💡 Quick Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💰 Salary Expectations"):
                prompt = "What should be my salary expectations based on my profile?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        with col2:
            if st.button("📈 Career Growth"):
                prompt = "What are the best career growth opportunities for me?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
        
        with col3:
            if st.button("🎓 Skill Development"):
                prompt = "What skills should I focus on developing next?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
    
    else:
        st.info("👆 Please upload your resume to start chatting with your career advisor")

elif page == "📊 Market Analytics":
    st.header("📊 Career Market Analytics")
    
    if st.session_state.resume_text:
        # Extract skills from resume
        skills_prompt = f"Extract the top 10 technical skills from this resume as a comma-separated list: {st.session_state.resume_text[:1000]}"
        skills_text = ask_gemini(skills_prompt, max_tokens=100)
        user_skills = [skill.strip().lower() for skill in skills_text.split(',')]
        
        # Experience level
        exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)', st.session_state.resume_text.lower())
        experience_level = int(exp_match.group(1)) if exp_match else 3
        
        tab1, tab2, tab3 = st.tabs(["💰 Salary Insights", "📈 Skill Demand", "🏢 Industry Trends"])
        
        with tab1:
            st.subheader("💰 Salary Analysis for Your Profile")
            salary_insights = st.session_state.analytics_engine.get_salary_insights(user_skills, experience_level)
            
            if 'stats' in salary_insights:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Median Salary", f"₹{salary_insights['stats']['median']:,.0f}")
                with col2:
                    st.metric("Average Salary", f"₹{salary_insights['stats']['mean']:,.0f}")
                with col3:
                    st.metric("75th Percentile", f"₹{salary_insights['stats']['percentile_75']:,.0f}")
                with col4:
                    st.metric("Sample Size", f"{salary_insights['stats']['sample_size']} jobs")
                
                st.plotly_chart(salary_insights['chart'], use_container_width=True)
            else:
                st.warning(salary_insights['message'])
        
        with tab2:
            st.subheader("📈 Skill Demand Analysis")
            skill_analysis = st.session_state.analytics_engine.get_skill_demand_analysis(user_skills)
            
            col1, col2 = st.columns(2)
            with col1:
                if skill_analysis['user_skills_chart']:
                    st.plotly_chart(skill_analysis['user_skills_chart'], use_container_width=True)
            with col2:
                st.plotly_chart(skill_analysis['market_trends_chart'], use_container_width=True)
        
        with tab3:
            st.subheader("🏢 Industry & Role Insights")
            industry_insights = st.session_state.analytics_engine.get_industry_insights(user_skills)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(industry_insights['industry_chart'], use_container_width=True)
            with col2:
                st.plotly_chart(industry_insights['roles_chart'], use_container_width=True)
    
    else:
        st.info("👆 Please upload your resume to view market analytics")

elif page == "🔍 Job Search":
    st.header("🔍 Intelligent Job Search")
    if st.session_state.resume_text:
        # Get job recommendations
        if st.button("🎯 Get Personalized Job Recommendations", type="primary"):
            with st.spinner("Analyzing your profile and finding matching jobs..."):
                # Extract keywords using AI
                keywords = ask_gemini(
                    f"Based on this resume, suggest the best job search keywords (comma-separated, max 5): \n\n{st.session_state.resume_text[:1000]}",
                    max_tokens=50
                )
                search_keywords = keywords.replace("\n", "").strip()
            
            st.success(f"🔍 Search Keywords: {search_keywords}")
            
            # Search using RAG
            with st.spinner("Finding relevant opportunities..."):
                rag_jobs = st.session_state.rag_engine.search_relevant_jobs(
                    f"{st.session_state.resume_text[:500]} {search_keywords}", 
                    n_results=10
                )
            
            st.subheader("🎯 AI-Matched Opportunities")
            for job in rag_jobs:
                with st.expander(f"🏢 {job['job_title']} - Relevance: {job['relevance_score']:.1%}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Skills:** {job['skills'][:150]}...")
                        st.write(f"**Experience:** {job['experience']}")
                    with col2:
                        st.write(f"**Industry:** {job['industry']}")
                        st.write(f"**Role Category:** {job['role_category']}")
                        st.write(f"**Salary:** {job['salary']}")
        
        # External job search - separate button
        st.subheader("🌐 Live Job Postings")
        
        if st.button("🔎 Get Job Recommendations"):
            with st.spinner("Fetching job recommendations..."):
                # Generate resume summary for keyword extraction
                summary = ask_gemini(
                    f"Provide a brief summary of this resume highlighting key skills and experience: \n\n{st.session_state.resume_text[:1000]}", 
                    max_tokens=200
                )
                
                

                search_keywords_clean = summary.replace("\n", "").strip()

            st.success(f"Extracted Job Keywords: {search_keywords_clean}")

            with st.spinner("Fetching jobs from LinkedIn ..."):
                linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows=60)

            st.markdown("---")
            st.header("💼 Top LinkedIn Jobs")

            if linkedin_jobs:
                for job in linkedin_jobs:
                    st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                    st.markdown(f"- 📍 {job.get('location')}")
                    st.markdown(f"- 🔗 [View Job]({job.get('link')})")
                    st.markdown("---")
            else:
                st.warning("No LinkedIn jobs found.")
    
    else:
        st.info("👆 Please upload your resume to search for jobs")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        🤖 Powered by RAG Technology & AI | Built with Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)


