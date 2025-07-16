import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from research_agent import research_agent
from query_refinement import refine_query

# 🔑 API
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def run_lit_review(raw_topic, progress_slot=None):
    """
    Run a literature review based on a voice or text input.
    Returns a refined query, a summary, and follow-up ready conversation history.
    """
    refined_topic = refine_query(raw_topic)
    summary, relevant_sources = research_agent(refined_topic, progress_slot=progress_slot)

    # Save to .txt:
    today = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"kanopik_lit_review_{today}.txt"
    lit_review_dir = os.path.join(os.path.dirname(__file__), "lit_reviews")
    os.makedirs(lit_review_dir, exist_ok=True)
    filepath = os.path.join(lit_review_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"📚 Kanopik Literature Review — {today}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"🔍 Topic: {refined_topic}\n\n")
        f.write(summary + "\n\n")
        f.write("📖 Sources:\n")
        for src in relevant_sources:
            f.write(f"- {src.get('title', 'No Title')} ({src.get('year', '')})\n")
            f.write(f"  {src.get('url', '')}\n\n")

    return summary, relevant_sources

def chat_with_kanopik():
    """
    Terminal-based interaction loop (for manual testing).
    """
    print("\n🧠 Welcome to Kanopik — your research assistant.\n")
    raw_topic = input("🔍 What topic would you like to research? ")
    summary, conversation_history = run_lit_review(raw_topic)

    print("\n📜 Research Summary:\n", summary)

    while True:
        follow_up = input("\n💬 Ask a follow-up question (or type 'exit' to quit): ").strip()
        if follow_up.lower() in ["exit", "quit", "stop"]:
            print("\n👋 Exiting Kanopik. Stay curious!\n")
            break

        conversation_history.append({"role": "user", "content": follow_up})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )

        reply = response.choices[0].message.content
        print("\n🤖 Kanopik:\n", reply)

        conversation_history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_kanopik()
