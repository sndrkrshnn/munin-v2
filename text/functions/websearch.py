import os 
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
load_dotenv()
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

GS_API = os.getenv("GOOGLE_SEARCH")
OA_API = os.getenv("OPENAI_API_KEY")

def google_search(query, relevant_searches=4):
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
        response = requests.get(result['link'])
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
        page_text = soup.get_text()
        cleaned_text = ' '.join(page_text.split())
        text_content.append(cleaned_text)
    db = embed_and_store(text_content)    
    return db


def embed_and_store(texts):
    embedding_function = OpenAIEmbeddings(api_key=OA_API)
    db = FAISS.from_texts(texts, embedding_function)
    return db
