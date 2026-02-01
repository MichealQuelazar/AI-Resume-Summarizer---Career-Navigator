"""
Configuration for Career Guidance RAG System Evaluation
"""

# Evaluation Dataset Settings
EVALUATION_DATASET_PATH = "evaluation dataset.csv"
SAMPLE_SIZE = 50  # Set to None to use full dataset
RANDOM_SEED = 42  # For reproducible sampling

# Sample Resume for Context-Aware Evaluation
SAMPLE_RESUME = """
Alex Johnson
Senior Software Engineer with 5 years of experience in full-stack development.
Expertise in Python, JavaScript, React, Node.js, and cloud technologies.
Experience with machine learning, data analysis, and system architecture.
Bachelor's degree in Computer Science, Master's in Software Engineering.
Skills: Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, 
Machine Learning, Data Analysis, SQL, MongoDB, Git, Agile Development
Previous roles: Junior Developer → Software Engineer → Senior Software Engineer
Looking to transition into Data Science or Machine Learning Engineering roles.
"""

# Evaluation Metrics Configuration
RELEVANCE_THRESHOLD = 0.3  # Threshold for considering a job relevant
TOP_K_JOBS = 5  # Number of top jobs to consider for retrieval metrics
SAVE_INTERMEDIATE_EVERY = 10  # Save intermediate results every N samples

# Output Configuration
RESULTS_CSV_PATH = "career_rag_evaluation_results.csv"
INTERMEDIATE_CSV_PATH = "career_evaluation_results_intermediate.csv"

# Performance Thresholds for Insights
EXCELLENT_CAREER_RELEVANCE = 0.7
GOOD_CAREER_RELEVANCE = 0.5
FAST_RESPONSE_TIME = 3.0  # seconds
ACCEPTABLE_RESPONSE_TIME = 5.0  # seconds

# Evaluation Categories
CAREER_TERMS = [
    'career', 'job', 'skill', 'experience', 'salary', 'role', 'position', 
    'industry', 'qualification', 'certification', 'training', 'development',
    'growth', 'promotion', 'transition', 'opportunity', 'market', 'demand'
]

# Test Configurations
QUICK_TEST_SAMPLE_SIZE = 5
MEDIUM_TEST_SAMPLE_SIZE = 20
FULL_TEST_SAMPLE_SIZE = None  