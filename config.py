"""
Configuration settings for AI Resume Summarizer & Career Navigator
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "AI Resume Summarizer & Career Navigator"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "RAG-based AI chatbot for career guidance and job recommendations"

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
JOBS_CSV_PATH = DATA_DIR / "jobs.csv"
CHROMA_DB_PATH = BASE_DIR / "chroma_db"

# AI Model settings
GEMINI_MODEL = "gemini-1.5-flash"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_TOKENS_DEFAULT = 500
TEMPERATURE_DEFAULT = 0.7

# RAG settings
VECTOR_DB_COLLECTION = "job_database"
SEARCH_RESULTS_LIMIT = 15
BATCH_SIZE = 100

# Job search settings
LINKEDIN_JOBS_LIMIT = 60
NAUKRI_JOBS_LIMIT = 60
DEFAULT_LOCATION = "india"

# UI settings
PAGE_TITLE = "AI Resume Summarizer & Career Navigator"
PAGE_ICON = "🤖"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Chat settings
MAX_CHAT_HISTORY = 10
CHAT_CONTEXT_LIMIT = 5

# Analytics settings
SALARY_PERCENTILES = [0.25, 0.5, 0.75]
TOP_SKILLS_LIMIT = 20
TOP_INDUSTRIES_LIMIT = 10

# Color schemes for UI
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#4facfe',
    'warning': '#f093fb',
    'error': '#f5576c',
    'info': '#00f2fe'
}

# Gradients for styled components
GRADIENTS = {
    'summary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'gaps': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'roadmap': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
}

# API endpoints and settings
API_SETTINGS = {
    'linkedin_actor': 'BHzefUZlZRKWxkTck',
    'naukri_actor': 'alpcnRV9YI9lYVPWk',
    'request_timeout': 30,
    'max_retries': 3
}

# Feature flags
FEATURES = {
    'enable_job_search': True,
    'enable_salary_insights': True,
    'enable_skill_analysis': True,
    'enable_chat': True,
    'enable_analytics': True
}

# Validation settings
VALIDATION = {
    'max_resume_size_mb': 10,
    'supported_formats': ['.pdf'],
    'min_resume_length': 100,
    'max_chat_message_length': 1000
}