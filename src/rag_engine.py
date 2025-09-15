import chromadb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class RAGEngine:
    def __init__(self, jobs_csv_path: str = "data/jobs.csv"):
        """Initialize RAG engine with job database and vector store"""
        self.jobs_csv_path = jobs_csv_path
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = None
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.jobs_df = None
        
        # Configure Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load the vector store with job data"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection("job_database")
            print("Loaded existing job database")
        except:
            # Create new collection if it doesn't exist
            self._create_vector_store()
    
    def _create_vector_store(self):
        """Create vector store from jobs CSV"""
        print("Creating new job database...")
        
        # Load jobs data
        self.jobs_df = pd.read_csv(self.jobs_csv_path)
        
        # Create collection
        self.collection = self.client.create_collection(
            name="job_database",
            metadata={"description": "Job listings with skills and requirements"}
        )
        
        # Process jobs in batches
        batch_size = 100
        for i in range(0, len(self.jobs_df), batch_size):
            batch = self.jobs_df.iloc[i:i+batch_size]
            
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in batch.iterrows():
                # Create document text combining job info
                doc_text = f"""
                Job Title: {row.get('Job Title', 'N/A')}
                Key Skills: {row.get('Key Skills', 'N/A')}
                Experience Required: {row.get('Job Experience Required', 'N/A')}
                Role Category: {row.get('Role Category', 'N/A')}
                Functional Area: {row.get('Functional Area', 'N/A')}
                Industry: {row.get('Industry', 'N/A')}
                Salary: {row.get('Job Salary', 'N/A')}
                """
                
                documents.append(doc_text.strip())
                metadatas.append({
                    'job_title': str(row.get('Job Title', 'N/A')),
                    'skills': str(row.get('Key Skills', 'N/A')),
                    'experience': str(row.get('Job Experience Required', 'N/A')),
                    'role_category': str(row.get('Role Category', 'N/A')),
                    'industry': str(row.get('Industry', 'N/A')),
                    'salary': str(row.get('Job Salary', 'N/A'))
                })
                ids.append(f"job_{idx}")
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Processed {min(i+batch_size, len(self.jobs_df))}/{len(self.jobs_df)} jobs")
        
        print("Job database created successfully!")
    
    def search_relevant_jobs(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search for relevant jobs based on query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        relevant_jobs = []
        for i, metadata in enumerate(results['metadatas'][0]):
            relevant_jobs.append({
                'job_title': metadata['job_title'],
                'skills': metadata['skills'],
                'experience': metadata['experience'],
                'role_category': metadata['role_category'],
                'industry': metadata['industry'],
                'salary': metadata['salary'],
                'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return relevant_jobs
    
    def get_career_insights(self, resume_text: str, user_query: str = None) -> Dict[str, Any]:
        """Generate comprehensive career insights using RAG"""
        
        # Extract key skills and experience from resume
        skills_prompt = f"""
        Extract the key skills, technologies, and experience level from this resume.
        Return as a structured summary:
        
        Resume: {resume_text[:2000]}...
        
        Format:
        Skills: [list of skills]
        Experience Level: [junior/mid/senior]
        Domain: [primary domain/field]
        """
        
        skills_analysis = self.model.generate_content(skills_prompt).text
        
        # Search for relevant jobs
        search_query = f"{skills_analysis} {user_query or ''}"
        relevant_jobs = self.search_relevant_jobs(search_query, n_results=15)
        
        # Generate insights based on relevant jobs
        jobs_context = "\n".join([
            f"Job: {job['job_title']} | Skills: {job['skills']} | Experience: {job['experience']} | Industry: {job['industry']}"
            for job in relevant_jobs[:10]
        ])
        
        insights_prompt = f"""
        Based on the resume analysis and current job market data, provide comprehensive career insights:
        
        Resume Analysis: {skills_analysis}
        
        Relevant Job Market Data:
        {jobs_context}
        
        User Query: {user_query or "General career guidance"}
        
        Provide insights on:
        1. Career progression opportunities
        2. Skill gaps and recommendations
        3. Salary expectations
        4. Industry trends
        5. Next career steps
        
        Be specific and actionable.
        """
        
        insights = self.model.generate_content(
            insights_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=800,
                temperature=0.7
            )
        ).text
        
        return {
            'insights': insights,
            'relevant_jobs': relevant_jobs,
            'skills_analysis': skills_analysis
        }
    
    def chat_with_career_advisor(self, resume_text: str, chat_history: List[Dict], user_message: str) -> str:
        """Interactive chat with career advisor"""
        
        # Get relevant context
        career_data = self.get_career_insights(resume_text, user_message)
        
        # Build conversation context
        conversation = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in chat_history[-5:]  # Last 5 messages for context
        ])
        
        chat_prompt = f"""
        You are an expert career advisor with access to current job market data. 
        
        Resume Summary: {career_data['skills_analysis'][:500]}
        
        Recent Job Market Insights:
        {chr(10).join([f"• {job['job_title']} - {job['skills'][:100]}" for job in career_data['relevant_jobs'][:5]])}
        
        Conversation History:
        {conversation}
        
        User Question: {user_message}
        
        Provide helpful, specific career advice based on the resume and current job market. 
        Be conversational and supportive.
        """
        
        response = self.model.generate_content(
            chat_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=600,
                temperature=0.8
            )
        ).text
        
        return response