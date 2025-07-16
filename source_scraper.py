import os
import requests
import arxiv
import time
from Bio import Entrez
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
Entrez.email = os.getenv("EMAIL_FOR_ENTREZ")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

def scrape_arxiv(query, max_results=10, since_date=None):
    client = arxiv.Client()

    if since_date is not None:
        arxiv_since_date = since_date.strftime("%Y%m%d0000")
        arxiv_end_date = datetime.now().strftime("%Y%m%d0000")
        date_filter = f"submittedDate:[{arxiv_since_date}+TO+{arxiv_end_date}]"
        full_query = f"all:{query}+AND+{date_filter}"
    else:
        full_query = f"all:{query}"

    search = arxiv.Search(
        query=full_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance if since_date is None else arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    try:
        return [{
            "title": result.title,
            "summary": result.summary,
            "url": result.entry_id,
            "year": str(result.published.year),
            "authors": [author.name for author in result.authors],
            "source": "arxiv"
        } for result in client.results(search)]
    except Exception as e:
        print(f"⚠️ ArXiv fetch failed: {e}")
        return []

def scrape_pubmed(query, max_results=10, since_date=None):
    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
    }

    if since_date:
        esearch_params.update({
            "mindate": since_date,
            "maxdate": datetime.now().strftime("%Y-%m-%d"),
            "datetype": "pdat"
        })

    handle = Entrez.esearch(**esearch_params)
    record = Entrez.read(handle)
    handle.close()
    ids = record.get("IdList", [])
    if not ids:
        return []

    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
    abstracts = Entrez.read(handle)
    handle.close()

    articles = []
    for i, article in enumerate(abstracts["PubmedArticle"]):
        try:
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = article["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0]
            url = f"https://pubmed.ncbi.nlm.nih.gov/{ids[i]}"

            # --- Authors --- #
            author_list = article["MedlineCitation"]["Article"].get("AuthorList", [])
            authors = []
            for author in author_list:
                if "LastName" in author and "Initials" in author:
                    authors.append(f"{author['LastName']}, {author['Initials']}")
            if not authors:
                authors = ["Unknown"]

            # --- Year --- #
            pub_date = article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"].get("PubDate", {})
            year = pub_date.get("Year", "unknown")
            if isinstance(year, int):
                year = str(year)

            articles.append({
                "title": title,
                "summary": abstract,
                "url": url,
                "source": "pubmed",
                "year": year,
                "authors": authors
            })
        except Exception:
            continue
    return articles

def scrape_semantic_scholar(query, max_results=10, since_date=None):
    time.sleep(1.1) # to avoid rate limit
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    since_date = (datetime.now().date() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    params = {
    "query": query,
    "limit": max_results,
    "fields": "title,abstract,authors,year,publicationDate,url"
    }
    if since_date:
        params["publicationDateOrYear"] = f"{since_date}:"

    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ Semantic Scholar API error: {response.status_code}")
        return []

    papers = []
    for item in response.json().get("data", []):
        title = item.get("title", "Untitled")
        abstract = item.get("abstract", "No abstract available.")
        url = item.get("url", "")
        year = item.get("year", "unknown")
        authors_raw = item.get("authors", [])
        authors = [f"{a.get('name')}" for a in authors_raw if a.get("name")]

        papers.append({
            "title": title,
            "summary": abstract,
            "url": url,
            "year": str(year),
            "authors": authors,
            "source": "semantic_scholar"
        })
    return papers

def scrape_biorxiv(query, max_results=10, since_date=None):
    print("⚠️ bioRxiv scraping not yet implemented. Falling back to Semantic Scholar.")
    return scrape_semantic_scholar(query, max_results)

def scrape_ssrn(query, max_results=10, since_date=None):
    print("⚠️ SSRN scraping not yet implemented. Falling back to Semantic Scholar.")
    return scrape_semantic_scholar(query, max_results)

def scrape_nber(query, max_results=10, since_date=None):
    print("⚠️ NBER scraping not yet implemented. Falling back to Semantic Scholar.")
    return scrape_semantic_scholar(query, max_results)

def scrape_repec(query, max_results=10, since_date=None):
    print("⚠️ RePEc scraping not yet implemented. Falling back to Semantic Scholar.")
    return scrape_semantic_scholar(query, max_results)

def unsupported_scrape_warning(source):
    print(f"⚠️ '{source}' is not yet implemented. Skipping.")
    return []

def fetch_from_sources(query, selected_sources, since_date=None):
    collected_data = []
    for source in selected_sources:
        print(f"🔍 Fetching from {source}...")
        source = source.lower()

        if source == "arxiv":
            collected_data.extend(scrape_arxiv(query, since_date=since_date))
        elif source == "pubmed":
            collected_data.extend(scrape_pubmed(query))
        elif source == "semantic_scholar":
            collected_data.extend(scrape_semantic_scholar(query, since_date=since_date))
        
        # not supported yet:
        elif source == "biorxiv":
            collected_data.extend(scrape_biorxiv(query, since_date=since_date))
        elif source == "ssrn":
            collected_data.extend(scrape_ssrn(query, since_date=since_date))
        elif source == "nber":
            collected_data.extend(scrape_nber(query, since_date=since_date))
        elif source == "repec":
            collected_data.extend(scrape_repec(query, since_date=since_date))
        elif source in ["sciencedirect", "springerlink", "ieee_xplore"]:
            collected_data.extend(scrape_semantic_scholar(query, since_date=since_date))

        else:
            collected_data.extend(unsupported_scrape_warning(source))

    return collected_data

if __name__ == "__main__":
    query = input("Enter a research topic: ")
    sources = ["arxiv", "pubmed", "semantic_scholar"]
    results = fetch_from_sources(query, sources)
    print(f"\n📄 Retrieved {len(results)} papers total:\n")
    for i, paper in enumerate(results, start=1):
        print(f"{i}. [{paper['source'].upper()}] {paper['title']}")
