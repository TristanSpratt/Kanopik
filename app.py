import streamlit as st
import os
from datetime import datetime
from lit_review import run_lit_review
from weekly_digest import generate_weekly_digest, USER_TOPICS
from voice_input import listen_to_voice_command
from voice_output import speak_text

st.set_page_config(page_title="Kanopik - Your Research Assistant", layout="centered")

# --- TITLE & SUBTITLE --- #
st.markdown("<h1 style='text-align: center; font-size: 60px;'>Kanopik</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>your literature review AI assistant</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- CHOICE ROW: What & How --- #
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5>1️⃣ What would you like to do?</h5>", unsafe_allow_html=True)
    mode = st.radio("", ["Literature Review", "Weekly Digest"], key="mode")

with col2:
    st.markdown("<h5>2️⃣ How do you want to interact?</h5>", unsafe_allow_html=True)
    interaction_mode = st.radio("", ["Text", "Voice"], key="interaction_mode")

# --- INPUT FIELD --- #
query = None
if mode == "Literature Review":
    st.subheader("📚 Literature Review")

    if interaction_mode == "Voice":
        if st.button("🎤 Start Recording"):
            query = listen_to_voice_command()
            if query:
                st.success(f"✅ You said: {query}")
            else:
                st.error("❌ Sorry, I didn't understand that.")
    else:
        query = st.text_input("Enter your research question:")

    if query:
        progress_placeholder = st.empty()
        with st.spinner("📡 Researching..."):
            summary, relevant_sources = run_lit_review(query, progress_slot=progress_placeholder)
            progress_placeholder.empty()

        st.markdown("---")
        st.markdown(summary)

        if interaction_mode == "Voice":
            speak_text(summary)

        # Study Explorer
        with st.expander("🔎 Dive deeper into individual studies"):
            for study in relevant_sources:
                authors = study.get('authors', [])
                if isinstance(authors, str):
                    authors = [authors]
                if len(authors) > 2:
                    author_display = f"{authors[0].split(',')[0]} et al."
                elif len(authors) == 2:
                    author_display = f"{authors[0].split(',')[0]} and {authors[1].split(',')[0]}"
                elif authors:
                    author_display = authors[0].split(',')[0]
                else:
                    author_display = "Unknown"
                year = study.get('year', 'unknown')
                st.markdown(f"**{study['title']}** ({author_display}, {year})")
                st.markdown(f"*Source: {study.get('source', 'unknown').capitalize()}*")
                st.markdown(study.get("summary") or "No summary available.")
                st.markdown(f"[🔗 View Full Study]({study.get('url', '#')})")
                st.markdown("---")

elif mode == "Weekly Digest":
    st.subheader("📅 Weekly Digest")

    if st.button("Generate Today's Digest"):
        with st.spinner("📰 Scanning new research..."):
            progress_placeholder = st.empty()
            digest_path, topic_results = generate_weekly_digest(USER_TOPICS, progress_slot=progress_placeholder)
            progress_placeholder.empty()

        today = datetime.now().strftime("%Y-%m-%d")
        digest_file = f"digests/kanopik_weekly_digest_{today}.txt"

        if os.path.exists(digest_file):
            with open(digest_file) as f:
                digest = f.read()
                st.text_area("📄 Today's Digest", digest, height=400)
                if interaction_mode == "Voice":
                    speak_text(digest)
            
            # Study Explorer
            with st.expander("🔎 Dive deeper into individual studies"):
                for topic, studies in topic_results.items():
                    st.markdown(f"### 🔬 Topic: {topic}")
                    for study in studies:
                        if not isinstance(study, dict):
                            continue
                        authors = study.get('authors', [])
                        if isinstance(authors, str):
                            authors = [authors]
                        if len(authors) > 2:
                            author_display = f"{authors[0].split(',')[0]} et al."
                        elif len(authors) == 2:
                            author_display = f"{authors[0].split(',')[0]} and {authors[1].split(',')[0]}"
                        elif authors:
                            author_display = authors[0].split(',')[0]
                        else:
                            author_display = "Unknown"
                        year = study.get('year', 'unknown')
                        st.markdown(f"**{study['title']}** ({author_display}, {year})")
                        st.markdown(f"*Source: {study.get('source', 'unknown').capitalize()}*")
                        st.markdown(study.get("summary") or "No summary available.")
                        st.markdown(f"[🔗 View Full Study]({study.get('url', '#')})")
                        st.markdown("---")
        else:
            st.error("❌ Digest file not found.")






