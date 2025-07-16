import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# 🔑 API
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Map categories to sources
SOURCE_CATEGORIES = {
    "biology": ["bioRxiv", "pubmed", "semantic_scholar"],
    "chemistry": ["sciencedirect", "semantic_scholar", "springerlink"],
    "computer science": ["arxiv", "ieee_xplore", "semantic_scholar"],
    "economics": ["nber", "repec", "ssrn"],
    "engineering": ["ieee_xplore", "semantic_scholar"],
    "environmental science": ["sciencedirect", "semantic_scholar", "springerlink"],
    "finance": ["nber", "ssrn"],
    "general science": ["sciencedirect", "semantic_scholar", "springerlink"],
    "math": ["arxiv", "semantic_scholar"],
    "medicine": ["pubmed", "semantic_scholar", "springerlink"],
    "neuroscience": ["arxiv", "bioRxiv", "pubmed", "semantic_scholar"],
    "physics": ["arxiv", "semantic_scholar"],
    "psychology": ["pubmed", "semantic_scholar", "ssrn"],
    "public health": ["pubmed", "sciencedirect"]
}


# Available categories
VALID_CATEGORIES = list(SOURCE_CATEGORIES.keys())

def classify_query(query):
    """
    Uses GPT to classify a user query into a scientific domain.
    """
    system_prompt = (
        "You are a classifier that categorizes research questions into fields of science.\n"
        f"Possible categories are: {', '.join(VALID_CATEGORIES)}.\n"
        "Return only the best matching category from that list — no explanations."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify this query: {query}"}
        ]
    )

    category = response.choices[0].message.content.strip().lower()
    return category if category in VALID_CATEGORIES else "general_science"

def select_sources(refined_query):
    """
    Determines the best sources based on category classification.
    """
    category = classify_query(refined_query)
    sources = SOURCE_CATEGORIES[category]

    return {"category": category, "sources": sources}

# Test script
if __name__ == "__main__":
    query = input("Enter a research topic: ")
    result = select_sources(query)
    print("\n📌 Category:", result["category"])
    print("🔍 Recommended Sources:", json.dumps(result["sources"], indent=2))
