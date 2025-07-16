import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from research_agent import research_agent

# Load API keys from .env
load_dotenv()

# Customize your interest topics here!
USER_TOPICS = [
    "Neuroscience research updates",
    "News about climate change and renewable energies",
    "Groundbreaking new research findings across all of science"
]

def generate_weekly_digest(topics, progress_slot=None):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"kanopik_weekly_digest_{today}.txt"
    digest_dir = os.path.join(os.getcwd(), "digests")
    os.makedirs(digest_dir, exist_ok=True)
    filepath = os.path.join(digest_dir, filename)

    print(f"\n Generating Kanopik Weekly Digest for {today}...\n")

    since_date = datetime.now().date() - timedelta(days=7)
    results = {}

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"🧠 Kanopik Weekly Digest — {today}\n")
        file.write("=" * 60 + "\n\n")

        for topic in topics:
            if progress_slot:
                progress_slot.markdown(f"🔍 Researching: **{topic}**")
            summary, sources = research_agent(topic, digest_mode=True, since_date=since_date, progress_slot=progress_slot)

            if progress_slot:
                progress_slot.markdown(f"✅ Finished topic: {topic} — {len(sources)} studies found\n")
            results[topic] = (summary, sources)
            file.write(f"🔹 Topic: {topic}\n\n{summary}\n")
            file.write("-" * 60 + "\n\n")

    print(f"✅ Digest saved to: {filepath}\n")
    return filepath, results

if __name__ == "__main__":
    generate_weekly_digest(USER_TOPICS)