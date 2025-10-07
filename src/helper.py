import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from groq import Groq


# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY. Please set it in your .env file.")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


# -----------------------------
# 2. Extract text from PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file.
    
    Args:
        uploaded_file (file-like): A file object (e.g. Streamlit upload).
        
    Returns:
        str: The extracted text.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# -----------------------------
# 3. Ask Groq
# -----------------------------
def ask_groq(prompt, model_name="llama-3.1-8b-instant", max_tokens=500, temperature=0.5):
    """
    Sends a prompt to the Groq API and returns the response.
    
    Args:
        prompt (str): The input text prompt.
        model_name (str): Groq model to use (e.g. 'llama3-8b-8192', 'mixtral-8x7b-32768').
        max_tokens (int): Maximum number of tokens in the response.
        temperature (float): Controls randomness.
        
    Returns:
        str: The response text.
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return response.choices[0].message.content.strip()
