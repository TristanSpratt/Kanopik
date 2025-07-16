import os
from dotenv import load_dotenv
import requests
import arxiv
from openai import OpenAI
from datetime import datetime
from source_selector import select_sources
from source_scraper import fetch_from_sources
from relevance_filter import filter_relevant_papers
import json
import re

# 🔑 API
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Normalize filename
def normalize_filename(text):
    return re.sub(r'[^a-zA-Z0-9_]+', '_', text.strip().lower())

def extract_year(study):
    for key in ["year", "published", "publication_date", "date"]:
        raw = study.get(key)
        if isinstance(raw, str):
            match = re.search(r"\b(19|20)\d{2}\b", raw)
            if match:
                return match.group(0)
        elif isinstance(raw, int):
            return str(raw)
    return "unknown"

# Save study metadata to JSON
def save_study_metadata(topic, studies):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{normalize_filename(topic)}_{date_str}.json"
    path = os.path.join("summary_sources", filename)

    json_data = []
    for study in studies:
        json_data.append({
            "title": study.get("title", "Untitled"),
            "summary": study.get("summary") or "No summary available.",
            "source": study.get("source", "unknown"),
            "authors": study.get("authors", []),
            "year": extract_year(study),
            "url": study.get("url", study.get("link", ""))
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    return path


def summarize_research(topic, sources, digest_mode=False, since_date=None):
    """
    Summarizes key findings from a list of sources using GPT-4o-mini, with structure and depth.
    """
    research_text = f"Research topic: {topic}\n\n"
    
    for i, s in enumerate(sources, start=1):
        
        summary_raw = s.get("summary")
        if summary_raw in [None, "None", "none", ""]:
            summary_raw = s.get("snippet")
        if summary_raw in [None, "None", "none", ""]:
            summary_raw = "No summary available."
        summary_text = summary_raw

        # source = s.get('source', 'unknown')
        year = s.get('year', 'unknown')
        title = s.get('title', 'Untitled')
        url = s.get('url', s.get('link', ''))

        authors = s.get("authors", [])
        if isinstance(authors, str):
            authors = [authors]
        if len(authors) > 2:
            citation_authors = f"{authors[0].split(',')[0]} et al."
        elif len(authors) == 2:
            citation_authors = f"{authors[0].split(',')[0]} and {authors[1].split(',')[0]}"
        elif authors:
            citation_authors = authors[0].split(',')[0]
        else:
            citation_authors = "Unknown"
        citation = f"{citation_authors}, {year}"

        research_text += (
            f"{i}. \"{title}\" ({citation}) — {summary_text}\n"
            f"   🔗 {url}\n\n"
    )

    system_prompt = (
        "You are Kanopik, a research assistant that writes structured and engaging research summaries. "
    )

    if digest_mode:
        system_prompt += (
            "Your goal is to write a clear, structured weekly digest of new scientific findings on the topic below. "
            "All studies provided were published in the past 7 days.\n\n"
            "For each study, include a 🔗 [Read More](URL) link using the link provided after the summary.\n\n"
            "Structure your summary as follows:\n"
            "1. A 1–2 sentence introduction on why this topic matters this week\n"
            "2. Key new findings, grouped logically if possible, with citations like 'In \"Paper Title\" by Smith et al., 2025...'\n"
            "3. A short conclusion with emerging questions, patterns, or potential next steps\n\n"
            "Keep it concise, insightful, and professional — like you're briefing a busy researcher."
        )
    else:
        system_prompt += (
            "Your goal is to help scientists and advanced students quickly understand the current state of knowledge on a topic.\n\n"
            "Given the list of studies below, write a summary with the following structure:\n"
            "1. A brief introduction on the topic and why it matters\n"
            "2. A detailed exploration of main findings across studies, highlighting important scientific details like methods, results, and participants if available.\n"
            "3. For each key point, ...mention the study title and authors (e.g., 'As shown in \"Hybrid CNN-SNN Corticomorphic Network\" by Wang et al., 2023...')\n"
            "4. A concluding paragraph that summarizes the direction of research and any open questions\n\n"
            # "For each paper, include a 🔗 [Read More](URL) link using the link provided after the summary.\n"
            "Write in clear, vivid language that flows like a narrative, but make sure to preserve technical accuracy."
        )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Summarize the following papers:\n\n{research_text}"}
        ]
    )

    return completion.choices[0].message.content

def research_agent(topic, progress_slot=None, digest_mode=False, since_date=None):
    """
    Runs the research assistant pipeline:
    1. Selects the best sources
    2. Fetches content from them
    3. Summarizes the findings
    """

    # Source selection:
    selection = select_sources(topic)
    sources_str = ', '.join(selection['sources'])
    if progress_slot:
        progress_slot.markdown(f"📌 Category: {selection['category']}")
        progress_slot.markdown(f"🔍 Searching in: {sources_str}")
    
    # Paper selection:
    all_sources = fetch_from_sources(topic, selection["sources"], since_date=since_date if digest_mode else None)
    if progress_slot:
        progress_slot.markdown(f"\n📄 Retrieved {len(all_sources)} total papers\n")
    if not all_sources or len(all_sources) == 0:
        return "⚠️ No sources found for this topic. Try changing your query.", []
    
    # Relevance filtering:
    if progress_slot:
        progress_slot.markdown("🧹 Filtering for relevance...")
    relevant_sources = filter_relevant_papers(all_sources, topic, digest_mode=digest_mode)
    
    # If no sources left, return:
    if not relevant_sources:
        if digest_mode:
            return "⚠️ No new relevant papers found on this topic this week.", []
        return "⚠️ No sufficiently relevant sources found. Try rephrasing your query.", []
    else:
        if progress_slot:
            progress_slot.markdown(f"🏆 {len(relevant_sources)} of {len(all_sources)} sources were considered most relevant.\n")

    if not digest_mode and len(relevant_sources) < 3:
        if progress_slot:
            progress_slot.markdown("⚠️ Very few relevant papers found. The topic may be underexplored, or the query may need rephrasing.")
    
    # Saving selected sources metadata to a json file (for future use):
    json_path = save_study_metadata(topic, relevant_sources)

    # Create and display summary:
    if progress_slot:
        progress_slot.markdown("📝 Summarizing findings...")
    summary = summarize_research(topic, relevant_sources, digest_mode=digest_mode, since_date=since_date)
    return summary, relevant_sources

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    result = research_agent(topic)
    print("\n📜 Research Summary:\n", result)
