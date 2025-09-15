import os
from dotenv import load_dotenv
import fitz  
import google.generativeai as genai


# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY. Please set it in your .env file.")


genai.configure(api_key=GOOGLE_API_KEY)


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
# 3. Ask Gemini
# -----------------------------


def ask_gemini(prompt, model_name="gemini-1.5-flash", max_tokens=500, temperature=0.5):
    """
    Sends a prompt to the Google Gemini API and returns the response.
    
    Args:
        prompt (str): The input text prompt.
        model_name (str): Gemini model to use.
        max_tokens (int): Maximum number of tokens in the response.
        temperature (float): Controls randomness.
        
    Returns:
        str: The response text.
    """
    model = genai.GenerativeModel(model_name)
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    
    return response.text.strip()
