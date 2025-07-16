import os
from dotenv import load_dotenv
from openai import OpenAI

# 🔑 API
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def filter_relevant_papers(papers, query, min_score=4,digest_mode=False):
    """
    Filters out irrelevant papers using GPT-based semantic scoring.

    Args:
        papers (list): List of dicts with keys "title" and "summary"
        query (str): Research question or topic
        min_score (int): Minimum 1-5 relevance score to keep a paper

    Returns:
        List of filtered papers
    """
    if digest_mode:
        min_score = 3
        
    filtered = []

    for paper in papers:
        text = f"Title: {paper['title']}\nAbstract: {paper.get('summary', '')}"
        prompt = (
            f"Rate how relevant the following paper is to the research question:\n"
            f"\"{query}\"\n\n"
            f"{text}\n\n"
            "Score the relevance from 1 (not relevant) to 5 (very relevant). Only respond with the number."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that scores scientific relevance."},
                    {"role": "user", "content": prompt}
                ]
            )

            score_text = response.choices[0].message.content.strip()
            score = int(score_text)

            if score >= min_score:
                filtered.append(paper)

        except Exception as e:
            print(f"⚠️ Skipping paper due to error: {e}")
            continue

    return filtered
