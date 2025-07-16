import os
from dotenv import load_dotenv
from openai import OpenAI

# 🔑 API
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def refine_query(user_query):
    """
    Converts a user question into a short, search-optimized phrase
    for scientific databases like arXiv, PubMed, and Semantic Scholar.
    """
    prompt = (
        f"The user has asked a research question: \"{user_query}\"\n\n"
        "Rewrite it into a concise, keyword-style search query that a researcher would enter into Google Scholar, PubMed, or arXiv. "
        "Include specific concepts and terms, but avoid full sentences, and don't add additional terms unless very relevant. "
        "Do not include explanations, punctuation, or bullet points. Output only the query string.\n\n"
        "Search query:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Kanopik, an assistant that reformulates user questions into concise scientific search queries."},
            {"role": "user", "content": prompt}
        ]
    )

    refined_query = response.choices[0].message.content.strip().strip('"')
    return refined_query

# Quick test loop
if __name__ == "__main__":
    user_input = input("🧠 Enter a research topic or question: ")
    refined = refine_query(user_input)
    print("\n🔍 Search Query:\n", refined)
