# Kanopik — Your Literature Review Assistant

Kanopik is an AI-powered research assistant that helps you quickly understand the current state of knowledge on any scientific topic. Designed for researchers, students, and curious minds, Kanopik finds and summarizes papers related to your research interests so you can stay at the treetop of humanity's knowledge forest.

---

## What Kanopik Does

Kanopik automates the hardest parts of a literature review:

- **Intelligent source selection** from trusted databases like arXiv, PubMed, and Semantic Scholar
- **Relevance filtering** to extract only the most meaningful information
- **Structured summarization** that reads like a narrative but retains scientific detail
- **Voice and text interaction** for seamless, hands-free use
- **Weekly digests** of new research in your chosen fields of interest
- **Study deep dives** that let you explore each paper in more detail

---

## Example Use Cases

- "What are the latest advances in carbon capture technology?"
- "What are the main theories of consciousness in computational neuroscience?"
- "How do planes fly?"

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/kanopik.git
cd kanopik
```

### 2. Create and Activate Environment (using conda)

```bash
conda create -n kanopik python=3.11
conda activate kanopik
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Kanopik requires access to external APIs. Copy `.env.example` and rename it `.env`, then fill in your own keys:

```bash
cp .env.example .env
```

Fill in these values:

```env
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key
EMAIL_FOR_ENTREZ=your_email_for_pubmed_access
```

> ⚠️ Some features require paid services (e.g., OpenAI and ElevenLabs). Without these, certain functionality like summarization or voice output may be unavailable.

---

## How to use Kanopik

### Launch the Web App (recommended)

After installing dependencies and setting up your .env file:

```bash
streamlit run app.py
```

This will launch the full Kanopik interface in your browser where you can:
- Choose between Literature Review or Weekly Digest
- Enter research questions via text or voice
- See a structured summary with clickable source links
- Explore a study deep dive panel under each result
- Optionally listen to summaries via text-to-speech

### Alternative: Use from Command Line

#### Literature Review Mode

```bash
python lit_review.py
```

Ask any research question via text or voice. Kanopik will:
- Select relevant sources
- Retrieve papers
- Filter based on relevance
- Summarize findings into a report

### Weekly Digest Mode

```bash
python weekly_digest.py
```

- Automatically runs a weekly review of your chosen research topics  
- Saves a timestamped `.txt` file in the `/digests` folder  
- Includes structured summaries + clickable source metadata  

---

To add your topics of interest for Kanopik's weekly digests, edit the USER_TOPICS list in weekly_digest.py.

## Currently Supported Sources

- arXiv  
- PubMed  
- Semantic Scholar

---

## Planned Enhancements

- Support for more sources (e.g., SpringerLink, IEEE Xplore, SSRN, RePEc)  
- fallback voice synthesis  
- Personalized research profiles  
- Audio-exportable digests for weekly listening  
- Streamlit web app + mobile UX

---

## 🙏 Attribution

This project uses:

- [OpenAI API](https://openai.com)  
- [Semantic Scholar API](https://api.semanticscholar.org)  
- [arXiv API](https://arxiv.org/help/api)  
- [PubMed Entrez](https://www.ncbi.nlm.nih.gov/books/NBK25501/)  
- [ElevenLabs API](https://www.elevenlabs.io)

> Please cite Semantic Scholar if publishing results that depend on its data.

---

## Contact

Built by Tristan Spratt  
📫 [LinkedIn](https://www.linkedin.com/in/tristanspratt/)  
💡 Open to ideas, issues, and pull requests!