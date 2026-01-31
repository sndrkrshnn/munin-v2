import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import numpy as np

load_dotenv()

GS_API = os.getenv("GOOGLE_SEARCH")
OA_API = os.getenv("OPENAI_API_KEY")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))


def get_embeddings(texts: list[str], client: OpenAI) -> list[list[float]]:
    """Get embeddings for a list of texts using OpenAI API."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]


def find_relevant_chunks(query: str, texts: list[str], client: OpenAI, top_k: int = 3, score_threshold: float = 0.5) -> list[str]:
    """Find the most relevant text chunks for a query using embeddings."""
    if not texts:
        return []
    
    # Get embeddings for query and all texts
    all_texts = [query] + texts
    embeddings = get_embeddings(all_texts, client)
    
    query_embedding = embeddings[0]
    text_embeddings = embeddings[1:]
    
    # Calculate similarities
    similarities = []
    for i, text_emb in enumerate(text_embeddings):
        score = cosine_similarity(query_embedding, text_emb)
        if score >= score_threshold:
            similarities.append((score, texts[i]))
    
    # Sort by similarity and return top_k
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in similarities[:top_k]]


def google_search(query: str, relevant_searches: int = 4) -> list[str]:
    """
    Search Google and return the text content from the top results.
    
    Args:
        query: The search query
        relevant_searches: Number of search results to fetch
        
    Returns:
        List of text content from the search results
    """
    search_engine_id = "e1a610dc9dff64f06"
    search_url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'q': query,
        'key': GS_API,
        'cx': search_engine_id,
        'num': relevant_searches
    }

    response = requests.get(search_url, params=params)
    search_results = response.json()

    results = []
    if "items" in search_results:
        for item in search_results["items"]:
            title = item["title"]
            snippet = item["snippet"]
            link = item["link"]
            results.append({
                "title": title,
                "snippet": snippet,
                "link": link
            })
    
    text_content = []
    for result in results:
        try:
            response = requests.get(result['link'], timeout=10)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            page_text = soup.get_text()
            cleaned_text = ' '.join(page_text.split())
            # Limit text length to avoid token limits
            if len(cleaned_text) > 8000:
                cleaned_text = cleaned_text[:8000]
            text_content.append(cleaned_text)
        except Exception:
            # If we can't fetch a page, use the snippet instead
            text_content.append(f"{result['title']}: {result['snippet']}")
    
    return text_content
