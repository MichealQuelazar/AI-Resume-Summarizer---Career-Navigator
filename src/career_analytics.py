import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
from typing import Dict, List, Any


class CareerAnalytics:
    def __init__(self, jobs_csv_path: str = "data/jobs.csv"):
        """Initialize career analytics with job data"""
        self.jobs_df = pd.read_csv(jobs_csv_path)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess job data for analytics"""
        # Clean salary data
        self.jobs_df['salary_clean'] = self.jobs_df['Job Salary'].apply(self._extract_salary)
        
        # Extract experience years
        self.jobs_df['experience_years'] = self.jobs_df['Job Experience Required'].apply(self._extract_experience)
        
        # Clean skills data
        self.jobs_df['skills_list'] = self.jobs_df['Key Skills'].apply(self._extract_skills)
    
    def _extract_salary(self, salary_str):
        """Extract numeric salary (handle ranges too)"""
        if pd.isna(salary_str) or 'Not Disclosed' in str(salary_str):
            return None
        
        numbers = re.findall(r'[\d,]+', str(salary_str))
        if numbers:
            try:
                values = [int(num.replace(',', '')) for num in numbers]
                if len(values) >= 2:
                    return sum(values) // len(values)  # take average of range
                return values[0]
            except Exception:
                return None
        return None
    
    def _extract_experience(self, exp_str):
        """Extract years of experience (handle ranges too)"""
        if pd.isna(exp_str):
            return None
        
        numbers = re.findall(r'\d+', str(exp_str))
        if numbers:
            values = list(map(int, numbers))
            if len(values) >= 2:
                return sum(values) // len(values)  # average of range
            return values[0]
        return None
    
    def _extract_skills(self, skills_str):
        """Extract skills list from skills string"""
        if pd.isna(skills_str):
            return []
        
        skills = re.split(r'[|,;]+', str(skills_str))
        return [skill.strip().lower() for skill in skills if skill.strip()]
    
    def get_salary_insights(self, user_skills: List[str], experience_level: int = None) -> Dict[str, Any]:
        """Get salary insights based on user skills and experience"""
        
        relevant_jobs = self.jobs_df[
            self.jobs_df['skills_list'].apply(
                lambda skills: any(skill in user_skills for skill in skills)
            )
        ].copy()
        
        if experience_level:
            relevant_jobs = relevant_jobs[
                (relevant_jobs['experience_years'] >= experience_level - 2) &
                (relevant_jobs['experience_years'] <= experience_level + 2)
            ]
        
        salary_data = relevant_jobs['salary_clean'].dropna()
        
        if len(salary_data) == 0:
            return {"message": "No salary data available for your profile"}
        
        salary_stats = {
            'median': salary_data.median(),
            'mean': salary_data.mean(),
            'min': salary_data.min(),
            'max': salary_data.max(),
            'percentile_25': salary_data.quantile(0.25),
            'percentile_75': salary_data.quantile(0.75),
            'sample_size': len(salary_data)
        }
        
        fig = px.histogram(
            salary_data, 
            nbins=20,
            title="Salary Distribution for Your Profile",
            labels={'value': 'Salary (INR)', 'count': 'Number of Jobs'}
        )
        fig.update_layout(template="plotly_white")
        
        return {
            'stats': salary_stats,
            'chart': fig,
            'relevant_jobs_count': len(relevant_jobs)
        }
    
    def get_skill_demand_analysis(self, user_skills: List[str]) -> Dict[str, Any]:
        """Analyze demand for user skills in job market"""
        
        all_skills = []
        for skills_list in self.jobs_df['skills_list']:
            all_skills.extend(skills_list)
        
        skill_counts = Counter(all_skills)
        
        user_skill_demand = {}
        for skill in user_skills:
            skill_lower = skill.lower()
            demand = skill_counts.get(skill_lower, 0)
            user_skill_demand[skill] = demand
        
        top_skills = dict(skill_counts.most_common(20))
        
        if user_skill_demand:
            fig_user = px.bar(
                x=list(user_skill_demand.keys()),
                y=list(user_skill_demand.values()),
                title="Demand for Your Skills",
                labels={'x': 'Skills', 'y': 'Job Postings Count'}
            )
            fig_user.update_layout(template="plotly_white")
        else:
            fig_user = None
        
        fig_market = px.bar(
            x=list(top_skills.keys())[:15],
            y=list(top_skills.values())[:15],
            title="Top 15 In-Demand Skills in Market",
            labels={'x': 'Skills', 'y': 'Job Postings Count'}
        )
        fig_market.update_layout(
            template="plotly_white",
            xaxis=dict(tickangle=45)
        )
        
        return {
            'user_skill_demand': user_skill_demand,
            'top_market_skills': top_skills,
            'user_skills_chart': fig_user,
            'market_trends_chart': fig_market
        }
    
    def get_industry_insights(self, user_skills: List[str]) -> Dict[str, Any]:
        """Get industry insights based on user skills"""
        
        relevant_jobs = self.jobs_df[
            self.jobs_df['skills_list'].apply(
                lambda skills: any(skill in user_skills for skill in skills)
            )
        ]
        
        industry_counts = relevant_jobs['Industry'].value_counts().head(10)
        role_counts = relevant_jobs['Role Category'].value_counts().head(10)
        
        fig_industry = px.pie(
            values=industry_counts.values,
            names=industry_counts.index,
            title="Industry Distribution for Your Skills"
        )
        fig_industry.update_layout(template="plotly_white")
        
        fig_roles = px.bar(
            x=role_counts.values,
            y=role_counts.index,
            orientation='h',
            title="Top Role Categories for Your Skills",
            labels={'x': 'Number of Jobs', 'y': 'Role Category'}
        )
        fig_roles.update_layout(template="plotly_white")
        
        return {
            'industry_distribution': industry_counts.to_dict(),
            'role_distribution': role_counts.to_dict(),
            'industry_chart': fig_industry,
            'roles_chart': fig_roles
        }
    
    def get_career_progression_path(self, current_role: str, experience_level: int) -> Dict[str, Any]:
        """Suggest career progression paths"""
        
        similar_roles = self.jobs_df[
            self.jobs_df['Job Title'].str.contains(current_role, case=False, na=False)
        ]
        
        progression_data = {}
        for exp_range in ['0-2', '3-5', '6-10', '10+']:
            if exp_range == '0-2':
                jobs = similar_roles[similar_roles['experience_years'] <= 2]
            elif exp_range == '3-5':
                jobs = similar_roles[
                    (similar_roles['experience_years'] >= 3) & 
                    (similar_roles['experience_years'] <= 5)
                ]
            elif exp_range == '6-10':
                jobs = similar_roles[
                    (similar_roles['experience_years'] >= 6) & 
                    (similar_roles['experience_years'] <= 10)
                ]
            else:
                jobs = similar_roles[similar_roles['experience_years'] > 10]
            
            if len(jobs) > 0:
                progression_data[exp_range] = {
                    'common_titles': jobs['Job Title'].value_counts().head(5).to_dict(),
                    'avg_salary': jobs['salary_clean'].mean() if jobs['salary_clean'].notna().any() else None,
                    'top_skills': Counter([skill for skills in jobs['skills_list'] for skill in skills]).most_common(10)
                }
        
        return progression_data
