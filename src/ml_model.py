"""
Custom ML Model for Resume Scoring and Job Matching
Integrates with existing RAG system without modifying core functionality
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle
import os
from typing import Dict, List, Tuple, Any
import re


class ResumeJobMatchingModel:
    """
    Custom ML model for intelligent resume-job matching and scoring
    Uses TF-IDF vectorization and cosine similarity with custom scoring logic
    """
    
    def __init__(self, jobs_csv_path: str = "data/jobs.csv"):
        """Initialize the ML model"""
        self.jobs_df = pd.read_csv(jobs_csv_path)
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2
        )
        self.scaler = StandardScaler()
        self.job_vectors = None
        self.model_trained = False
        
        self._train_model()
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract numerical features from text"""
        features = {}
        
        # Experience indicators
        exp_matches = re.findall(r'(\d+)\s*(?:years?|yrs?)', text.lower())
        features['experience_years'] = max([int(x) for x in exp_matches]) if exp_matches else 0
        
        # Education level
        education_keywords = {
            'phd': 5, 'doctorate': 5,
            'masters': 4, 'mba': 4, 'ms': 4,
            'bachelor': 3, 'btech': 3, 'be': 3,
            'diploma': 2
        }
        features['education_level'] = max(
            [score for keyword, score in education_keywords.items() if keyword in text.lower()],
            default=1
        )
        
        # Technical skills count
        tech_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
            'kubernetes', 'react', 'angular', 'node', 'machine learning',
            'data science', 'ai', 'deep learning', 'tensorflow', 'pytorch'
        ]
        features['tech_skills_count'] = sum(1 for keyword in tech_keywords if keyword in text.lower())
        
        # Certifications
        cert_keywords = ['certified', 'certification', 'certificate']
        features['has_certifications'] = 1 if any(kw in text.lower() for kw in cert_keywords) else 0
        
        # Leadership indicators
        leadership_keywords = ['lead', 'manager', 'director', 'head', 'chief', 'senior']
        features['leadership_score'] = sum(1 for kw in leadership_keywords if kw in text.lower())
        
        return features
    
    def _train_model(self):
        """Train the model on job data"""
        print("Training ML model...")
        
        # Prepare job documents
        self.jobs_df['combined_text'] = (
            self.jobs_df['Job Title'].fillna('') + ' ' +
            self.jobs_df['Key Skills'].fillna('') + ' ' +
            self.jobs_df['Role Category'].fillna('') + ' ' +
            self.jobs_df['Functional Area'].fillna('')
        )
        
        self.jobs_df['processed_text'] = self.jobs_df['combined_text'].apply(self._preprocess_text)
        
        # Fit vectorizer and transform job data
        self.job_vectors = self.vectorizer.fit_transform(self.jobs_df['processed_text'])
        
        self.model_trained = True
        print(f"ML model trained on {len(self.jobs_df)} jobs")
    
    def score_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Score a resume on multiple dimensions
        Returns comprehensive scoring metrics
        """
        processed_resume = self._preprocess_text(resume_text)
        resume_features = self._extract_features(resume_text)
        
        # Calculate scores
        scores = {
            'overall_score': 0.0,
            'experience_score': 0.0,
            'skills_score': 0.0,
            'education_score': 0.0,
            'completeness_score': 0.0,
            'market_readiness': 0.0
        }
        
        # Experience score (0-100)
        exp_years = resume_features['experience_years']
        scores['experience_score'] = min(100, (exp_years / 10) * 100)
        
        # Skills score (0-100)
        tech_count = resume_features['tech_skills_count']
        scores['skills_score'] = min(100, (tech_count / 15) * 100)
        
        # Education score (0-100)
        edu_level = resume_features['education_level']
        scores['education_score'] = (edu_level / 5) * 100
        
        # Completeness score (0-100)
        resume_length = len(resume_text.split())
        has_contact = any(kw in resume_text.lower() for kw in ['email', 'phone', 'linkedin'])
        has_summary = len(resume_text) > 200
        completeness_factors = [
            resume_length > 100,
            has_contact,
            has_summary,
            resume_features['has_certifications'],
            exp_years > 0
        ]
        scores['completeness_score'] = (sum(completeness_factors) / len(completeness_factors)) * 100
        
        # Market readiness (0-100)
        scores['market_readiness'] = (
            scores['experience_score'] * 0.3 +
            scores['skills_score'] * 0.4 +
            scores['education_score'] * 0.2 +
            scores['completeness_score'] * 0.1
        )
        
        # Overall score (weighted average)
        scores['overall_score'] = (
            scores['experience_score'] * 0.25 +
            scores['skills_score'] * 0.35 +
            scores['education_score'] * 0.20 +
            scores['completeness_score'] * 0.10 +
            scores['market_readiness'] * 0.10
        )
        
        return {
            'scores': scores,
            'features': resume_features,
            'recommendations': self._generate_recommendations(scores, resume_features)
        }
    
    def match_jobs(self, resume_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find top matching jobs for a resume
        Returns ranked list of job matches with scores
        """
        if not self.model_trained:
            raise ValueError("Model not trained yet")
        
        # Preprocess and vectorize resume
        processed_resume = self._preprocess_text(resume_text)
        resume_vector = self.vectorizer.transform([processed_resume])
        
        # Calculate cosine similarity with all jobs
        similarities = cosine_similarity(resume_vector, self.job_vectors)[0]
        
        # Get top K matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matches = []
        for idx in top_indices:
            job = self.jobs_df.iloc[idx]
            match_score = float(similarities[idx]) * 100
            
            matches.append({
                'job_id': int(job['Job Id']) if 'Job Id' in job else idx,
                'job_title': job['Job Title'],
                'company': job.get('Company', 'N/A'),
                'location': job.get('Location', 'N/A'),
                'role_category': job.get('Role Category', 'N/A'),
                'key_skills': job.get('Key Skills', 'N/A'),
                'match_score': round(match_score, 2),
                'similarity': round(float(similarities[idx]), 4)
            })
        
        return matches
    
    def analyze_skill_gaps(self, resume_text: str, target_job_title: str) -> Dict[str, Any]:
        """
        Analyze skill gaps between resume and target job
        Returns missing skills and recommendations
        """
        # Find jobs matching the target title
        matching_jobs = self.jobs_df[
            self.jobs_df['Job Title'].str.contains(target_job_title, case=False, na=False)
        ]
        
        if matching_jobs.empty:
            return {
                'target_job': target_job_title,
                'found': False,
                'message': 'No matching jobs found for this title'
            }
        
        # Extract skills from resume
        resume_lower = resume_text.lower()
        resume_skills = set()
        
        # Extract skills from target jobs
        target_skills = set()
        for _, job in matching_jobs.iterrows():
            if pd.notna(job.get('Key Skills')):
                skills = str(job['Key Skills']).split(',')
                target_skills.update([s.strip().lower() for s in skills])
        
        # Common tech skills to check
        all_skills = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
            'kubernetes', 'react', 'angular', 'node.js', 'machine learning',
            'data science', 'ai', 'deep learning', 'tensorflow', 'pytorch',
            'git', 'agile', 'scrum', 'ci/cd', 'rest api', 'microservices'
        ]
        
        for skill in all_skills:
            if skill in resume_lower:
                resume_skills.add(skill)
        
        # Find gaps
        missing_skills = target_skills - resume_skills
        matching_skills = target_skills & resume_skills
        
        return {
            'target_job': target_job_title,
            'found': True,
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills),
            'match_percentage': round(len(matching_skills) / len(target_skills) * 100, 2) if target_skills else 0,
            'recommendations': self._generate_skill_recommendations(missing_skills)
        }
    
    def _generate_recommendations(self, scores: Dict[str, float], features: Dict[str, float]) -> List[str]:
        """Generate personalized recommendations based on scores"""
        recommendations = []
        
        if scores['experience_score'] < 50:
            recommendations.append("Consider highlighting more work experience and quantifiable achievements")
        
        if scores['skills_score'] < 60:
            recommendations.append("Add more technical skills and tools you're proficient in")
        
        if scores['education_score'] < 60:
            recommendations.append("Include your educational qualifications and relevant coursework")
        
        if scores['completeness_score'] < 70:
            recommendations.append("Ensure your resume includes contact information, summary, and key sections")
        
        if features['has_certifications'] == 0:
            recommendations.append("Consider adding relevant certifications to strengthen your profile")
        
        if features['leadership_score'] == 0:
            recommendations.append("Highlight any leadership roles or team management experience")
        
        if not recommendations:
            recommendations.append("Your resume looks strong! Keep it updated with recent achievements")
        
        return recommendations
    
    def _generate_skill_recommendations(self, missing_skills: set) -> List[str]:
        """Generate recommendations for missing skills"""
        if not missing_skills:
            return ["You have all the key skills for this role!"]
        
        recommendations = []
        skill_list = list(missing_skills)[:5]  # Top 5 missing skills
        
        recommendations.append(f"Consider learning: {', '.join(skill_list)}")
        recommendations.append("Take online courses or certifications in these areas")
        recommendations.append("Work on projects that demonstrate these skills")
        
        return recommendations
    
    def save_model(self, filepath: str = "models/ml_model.pkl"):
        """Save the trained model to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'job_vectors': self.job_vectors,
            'jobs_df': self.jobs_df,
            'scaler': self.scaler
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = "models/ml_model.pkl"):
        """Load a trained model from disk"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.job_vectors = model_data['job_vectors']
        self.jobs_df = model_data['jobs_df']
        self.scaler = model_data['scaler']
        self.model_trained = True
        
        print(f"Model loaded from {filepath}")


def get_ml_model(jobs_csv_path: str = "data/jobs.csv") -> ResumeJobMatchingModel:
    """
    Factory function to get or create ML model instance
    """
    return ResumeJobMatchingModel(jobs_csv_path)


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = get_ml_model()
    
    # Example resume text
    sample_resume = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-234-567-8900
    
    Summary:
    Experienced Software Engineer with 5 years of experience in Python, machine learning,
    and cloud technologies. Proven track record in developing scalable applications.
    
    Experience:
    Senior Software Engineer at Tech Corp (3 years)
    - Developed ML models using Python, TensorFlow, and PyTorch
    - Deployed applications on AWS and Azure
    - Led a team of 4 developers
    
    Software Engineer at StartupXYZ (2 years)
    - Built REST APIs using Python and Node.js
    - Implemented CI/CD pipelines with Docker and Kubernetes
    
    Education:
    Bachelor of Technology in Computer Science
    
    Skills:
    Python, Java, JavaScript, SQL, AWS, Docker, Kubernetes, Machine Learning,
    TensorFlow, PyTorch, React, Git, Agile
    
    Certifications:
    - AWS Certified Solutions Architect
    - Google Cloud Professional
    """
    
    # Score resume
    print("\n=== Resume Scoring ===")
    scoring_result = model.score_resume(sample_resume)
    print(f"Overall Score: {scoring_result['scores']['overall_score']:.2f}/100")
    print(f"Experience Score: {scoring_result['scores']['experience_score']:.2f}/100")
    print(f"Skills Score: {scoring_result['scores']['skills_score']:.2f}/100")
    print(f"Education Score: {scoring_result['scores']['education_score']:.2f}/100")
    print(f"\nRecommendations:")
    for rec in scoring_result['recommendations']:
        print(f"  - {rec}")
    
    # Match jobs
    print("\n=== Top Job Matches ===")
    matches = model.match_jobs(sample_resume, top_k=3)
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match['job_title']}")
        print(f"   Company: {match['company']}")
        print(f"   Match Score: {match['match_score']:.2f}%")
        print(f"   Key Skills: {match['key_skills']}")
    
    # Analyze skill gaps
    print("\n=== Skill Gap Analysis ===")
    gap_analysis = model.analyze_skill_gaps(sample_resume, "Data Scientist")
    if gap_analysis['found']:
        print(f"Target Job: {gap_analysis['target_job']}")
        print(f"Match Percentage: {gap_analysis['match_percentage']:.2f}%")
        print(f"Missing Skills: {', '.join(gap_analysis['missing_skills'][:5])}")
