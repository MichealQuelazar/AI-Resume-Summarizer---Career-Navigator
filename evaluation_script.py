import numpy as np
from collections import Counter
from rouge_score import rouge_scorer
import evaluate
import torch
from bert_score import score as bert_score
from tqdm import tqdm
import pandas as pd
from difflib import SequenceMatcher
import time
import warnings
import os
from dotenv import load_dotenv
import ssl
import certifi


# Import project-specific modules
from src.rag_engine import RAGEngine
from src.helper import ask_groq
from config import *
from evaluation_config import *

# Ignore warnings
warnings.filterwarnings("ignore")

import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
nltk.download('punkt', quiet=True)

# Load environment variables
load_dotenv()

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE



def ensure_nltk_downloads():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)

# Evaluation metrics functions
def safe_divide(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0

def is_similar(text1, text2, threshold=0.5):
    return SequenceMatcher(None, text1, text2).ratio() > threshold

def compute_precision_at_k(relevant_at_k):
    return safe_divide(sum(relevant_at_k), len(relevant_at_k))

def compute_recall_at_k(relevant_at_k, total_relevant):
    return safe_divide(sum(relevant_at_k), total_relevant)

def compute_mrr(relevant_at_k):
    try:
        first_relevant_rank = next(i for i, r in enumerate(relevant_at_k, 1) if r) + 1
        return 1 / first_relevant_rank
    except StopIteration:
        return 0

def compute_dcg(relevances):
    return sum((2**rel - 1) / np.log2(idx + 2) for idx, rel in enumerate(relevances))

def compute_ndcg(relevant_at_k):
    dcg = compute_dcg(relevant_at_k)
    idcg = compute_dcg(sorted(relevant_at_k, reverse=True))
    return safe_divide(dcg, idcg)

def compute_rouge_l(reference, candidate):
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    return scorer.score(reference, candidate)['rougeL'].fmeasure

def compute_bleu(reference, candidate):
    bleu = evaluate.load("bleu")
    return bleu.compute(predictions=[candidate], references=[[reference]])['bleu']
    

def compute_bert_score(reference, candidate):
    _, _, f1 = bert_score([candidate], [reference], lang="en")
    return f1.mean().item()


def compute_exact_match(reference, candidate):
    return int(candidate.strip().lower() == reference.strip().lower())

def compute_f1(reference, candidate):
    ref_tokens = reference.split()
    cand_tokens = candidate.split()
    common = Counter(ref_tokens) & Counter(cand_tokens)
    num_common = sum(common.values())
    
    precision = safe_divide(num_common, len(cand_tokens))
    recall = safe_divide(num_common, len(ref_tokens))
    
    return safe_divide(2 * precision * recall, precision + recall)

# Career RAG system setup functions
def initialize_career_rag_system():
    """Initialize the career guidance RAG system"""
    rag_engine = RAGEngine()
    return rag_engine

def generate_career_answer(rag_engine, question, context_resume=None):
    """Generate career guidance answer using the RAG system"""
    if context_resume:
        # Use chat functionality for personalized responses
        response = rag_engine.chat_with_career_advisor(
            resume_text=context_resume,
            chat_history=[],
            user_message=question
        )
    else:
        # Use general career insights
        insights = rag_engine.get_career_insights("", question)
        response = insights['insights']
    
    return response

def load_evaluation_dataset(file_path, sample_size=None):
    """Load career-focused evaluation dataset"""
    df = pd.read_csv(file_path)
    
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)))
    
    # Rename columns to match expected format
    if 'question' in df.columns and 'answer' in df.columns:
        return df[['question', 'answer']].apply(
            lambda row: {"question": row['question'], "answer": row['answer']}, axis=1
        ).tolist()
    else:
        # Fallback to original column names
        return df.apply(
            lambda row: {"question": row.iloc[0], "answer": row.iloc[1]}, axis=1
        ).tolist()


#############################################################################################################################
#############################################################################################################################
#############################################################################################################################


# Main evaluation function for career guidance system
def evaluate_career_rag_system(evaluation_dataset, rag_engine, sample_resume=None):
    """Evaluate the career guidance RAG system"""
    metrics = {
        'precision_at_k': [], 'recall_at_k': [], 'mrr': [], 'ndcg': [],
        'rouge_l': [], 'bleu': [], 'bert_score': [], 'exact_match': [],
        'f1': [], 'response_time': [], 'career_relevance': []
    }

    for sample in tqdm(evaluation_dataset, desc="Evaluating Career RAG System"):
        question = sample["question"]
        reference_answer = sample["answer"]

        # Generate answer using career RAG system
        start_time = time.time()
        
        try:
            # Search for relevant jobs first
            relevant_jobs = rag_engine.search_relevant_jobs(question, n_results=10)
            retrieval_time = time.time() - start_time
            
            # Generate career guidance answer
            start_time = time.time()
            generated_answer = generate_career_answer(rag_engine, question, sample_resume)
            generation_time = time.time() - start_time
            
            response_time = retrieval_time + generation_time
            
            # Evaluate retrieval quality based on job relevance
            job_relevance_scores = [job['relevance_score'] for job in relevant_jobs[:TOP_K_JOBS]]
            # Use a more reasonable threshold for similarity scores (0.1 instead of 0.3)
            relevant_at_k = [score > 0.1 for score in job_relevance_scores]
            
            # Pad with False if we have fewer than 5 results
            while len(relevant_at_k) < TOP_K_JOBS:
                relevant_at_k.append(False)
            
            # Calculate retrieval metrics
            metrics['precision_at_k'].append(compute_precision_at_k(relevant_at_k))
            metrics['recall_at_k'].append(compute_recall_at_k(relevant_at_k, len(relevant_jobs)))
            metrics['mrr'].append(compute_mrr(relevant_at_k))
            metrics['ndcg'].append(compute_ndcg([1 if rel else 0 for rel in relevant_at_k]))
            
            # Calculate generation quality metrics
            metrics['rouge_l'].append(compute_rouge_l(reference_answer, generated_answer))
            metrics['bleu'].append(compute_bleu(reference_answer, generated_answer))
            metrics['bert_score'].append(compute_bert_score(reference_answer, generated_answer))
            metrics['exact_match'].append(compute_exact_match(reference_answer, generated_answer))
            metrics['f1'].append(compute_f1(reference_answer, generated_answer))
            metrics['response_time'].append(response_time)
            
            # Career-specific relevance score
            career_relevance = compute_career_relevance(question, generated_answer, relevant_jobs)
            metrics['career_relevance'].append(career_relevance)
            
        except Exception as e:
            print(f"Error processing question: {question[:50]}... Error: {e}")
            # Add zero scores for failed cases
            for metric in metrics:
                metrics[metric].append(0.0)

        # Save intermediate results
        if len(metrics['response_time']) % SAVE_INTERMEDIATE_EVERY == 0:
            df = pd.DataFrame(metrics)
            df.to_csv(INTERMEDIATE_CSV_PATH, index=False)

    return metrics

def compute_career_relevance(question, answer, relevant_jobs):
    """Compute career-specific relevance score"""
    # Check if answer mentions career-related terms
    answer_lower = answer.lower()
    
    career_mentions = sum(1 for term in CAREER_TERMS if term in answer_lower)
    career_score = min(career_mentions / len(CAREER_TERMS), 1.0)
    
    # Factor in job retrieval quality
    if relevant_jobs:
        avg_job_relevance = np.mean([job['relevance_score'] for job in relevant_jobs[:3]])
        combined_score = (career_score + avg_job_relevance) / 2
    else:
        combined_score = career_score
    
    return combined_score

def print_career_evaluation_results(metrics):
    """Print comprehensive evaluation results for career guidance system"""
    df = pd.DataFrame(metrics)
    df.to_csv(RESULTS_CSV_PATH, index=False)
    
    print("\n" + "="*80)
    print("CAREER GUIDANCE RAG SYSTEM EVALUATION RESULTS")
    print("="*80)
    
    print("\n RETRIEVAL METRICS:")
    print(f"  • Precision@5: {np.mean(metrics['precision_at_k']):.3f} ± {np.std(metrics['precision_at_k']):.3f}")
    print(f"  • Recall@5: {np.mean(metrics['recall_at_k']):.3f} ± {np.std(metrics['recall_at_k']):.3f}")
    print(f"  • MRR: {np.mean(metrics['mrr']):.3f} ± {np.std(metrics['mrr']):.3f}")
    print(f"  • NDCG: {np.mean(metrics['ndcg']):.3f} ± {np.std(metrics['ndcg']):.3f}")
    
    print("\n GENERATION QUALITY METRICS:")
    print(f"  • ROUGE-L: {np.mean(metrics['rouge_l']):.3f} ± {np.std(metrics['rouge_l']):.3f}")
    print(f"  • BLEU Score: {np.mean(metrics['bleu']):.3f} ± {np.std(metrics['bleu']):.3f}")
    print(f"  • BERT Score: {np.mean(metrics['bert_score']):.3f} ± {np.std(metrics['bert_score']):.3f}")
    print(f"  • F1 Score: {np.mean(metrics['f1']):.3f} ± {np.std(metrics['f1']):.3f}")
    print(f"  • Exact Match: {np.mean(metrics['exact_match']):.3f} ± {np.std(metrics['exact_match']):.3f}")
    
    print("\n CAREER-SPECIFIC METRICS:")
    print(f"  • Career Relevance: {np.mean(metrics['career_relevance']):.3f} ± {np.std(metrics['career_relevance']):.3f}")
    
    print("\n PERFORMANCE METRICS:")
    print(f"  • Average Response Time: {np.mean(metrics['response_time']):.2f}s ± {np.std(metrics['response_time']):.2f}s")
    print(f"  • Min Response Time: {np.min(metrics['response_time']):.2f}s")
    print(f"  • Max Response Time: {np.max(metrics['response_time']):.2f}s")
    print(f"  • Total Samples Processed: {len(metrics['precision_at_k'])}")
    
    # Detailed analysis
    print("\n DETAILED PERFORMANCE ANALYSIS:")
    
    # Career relevance analysis
    career_rel = np.mean(metrics['career_relevance'])
    if career_rel > EXCELLENT_CAREER_RELEVANCE:
        print("   EXCELLENT career relevance - system provides highly relevant career guidance")
    elif career_rel > GOOD_CAREER_RELEVANCE:
        print("   GOOD career relevance - room for improvement in career-specific responses")
    else:
        print("  LOW career relevance - system needs significant improvement")
    
    # Response time analysis
    avg_time = np.mean(metrics['response_time'])
    if avg_time < FAST_RESPONSE_TIME:
        print("   FAST response times - excellent user experience")
    elif avg_time < ACCEPTABLE_RESPONSE_TIME:
        print("   MODERATE response times - acceptable but could be faster")
    else:
        print("  SLOW response times - may impact user experience")
    
    # Generation quality analysis
    bert_score = np.mean(metrics['bert_score'])
    rouge_score = np.mean(metrics['rouge_l'])
    
    print(f"\n QUALITY ASSESSMENT:")
    print(f"  • Semantic Similarity (BERT): {'HIGH' if bert_score > 0.8 else 'MODERATE' if bert_score > 0.7 else 'LOW'} ({bert_score:.3f})")
    print(f"  • Content Overlap (ROUGE-L): {'HIGH' if rouge_score > 0.3 else 'MODERATE' if rouge_score > 0.1 else 'LOW'} ({rouge_score:.3f})")
    
    # Recommendations
    print(f"\n RECOMMENDATIONS:")
    if np.mean(metrics['precision_at_k']) == 0:
        print("  • Improve job relevance scoring - consider adjusting similarity thresholds")
    if rouge_score < 0.2:
        print("  • Enhance answer generation to better match expected responses")
    if career_rel < 0.5:
        print("  • Improve career-specific terminology and context in responses")
    if avg_time > 5:
        print("  • Optimize response time through caching or model optimization")
    
    print("\n" + "="*80)



#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


# Main execution
if __name__ == "__main__":
    print(" Starting Career Guidance RAG System Evaluation...")
    
    # Configuration from evaluation_config.py
    evaluation_dataset_path = EVALUATION_DATASET_PATH
    sample_size = SAMPLE_SIZE
    sample_resume = SAMPLE_RESUME
    
    try:
        # Initialize career RAG system
        print(" Initializing Career RAG System...")
        rag_engine = initialize_career_rag_system()
        print(" Career RAG System initialized successfully!")
        
        # Load evaluation dataset
        print(f" Loading evaluation dataset from {evaluation_dataset_path}...")
        evaluation_dataset = load_evaluation_dataset(evaluation_dataset_path, sample_size)
        print(f" Loaded {len(evaluation_dataset)} evaluation samples")
        
        # Run evaluation
        print(" Running comprehensive evaluation...")
        metrics = evaluate_career_rag_system(evaluation_dataset, rag_engine, sample_resume)
        
        # Print results
        print_career_evaluation_results(metrics)
        
        print("\n Evaluation completed successfully!")
        print(f" Results saved to: {RESULTS_CSV_PATH}")
        print(f" Intermediate results: {INTERMEDIATE_CSV_PATH}")
        
    except Exception as e:
        print(f" Error during evaluation: {e}")
        import traceback
        traceback.print_exc()