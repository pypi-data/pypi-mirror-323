import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import click
import llm
import sqlite_utils
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Get your Jina AI API key for free: https://jina.ai/?sui=apikey
JINA_API_KEY = os.getenv("JINA_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def user_dir():
    llm_user_path = os.environ.get("LLM_USER_PATH")
    if llm_user_path:
        path = Path(llm_user_path)
    else:
        path = Path(click.get_app_dir("io.datasette.llm"))
    path.mkdir(exist_ok=True, parents=True)
    return path

def logs_db_path():
    return user_dir() / "logs.db"

def jina_search(query: str, site: Optional[str] = None, days: Optional[int] = None) -> List[Dict]:
    """Web search with optional site and date filtering"""
    try:
        search_headers = HEADERS.copy()
        if site:
            search_headers["X-Site"] = site
        date_filter = ""
        if days:
            date_filter = f" after:{datetime.now() - timedelta(days=days):%Y-%m-%d}"

        response = requests.post(
            "https://s.jina.ai/",
            headers=search_headers,
            json={"q": f"{query}{date_filter}", "options": "Markdown"},
            timeout=30
        )
        response.raise_for_status()
        return [{
            "url": result["url"],
            "title": result["title"],
            "snippet": result["content"][:500]
        } for result in response.json()["data"][:5]]  # Increased to top 5 results
    except Exception as e:
        print(f"🔍 Search Error: {e}")
        return []

def process_url(url: str) -> Dict:
    """Advanced content extraction with reader API"""
    try:
        response = requests.post(
            "https://r.jina.ai/",
            headers={**HEADERS,
                    "X-With-Links-Summary": "true",
                    "X-With-Images-Summary": "true",
                    "X-Return-Format": "markdown"},
            json={"url": url},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()["data"]
        return {
            "url": url,
            "content": data["content"],
            "links": data.get("links", {}),
            "images": data.get("images", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"📖 Reader Error ({url}): {e}")
        return {}

def get_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text using Embeddings API"""
    try:
        response = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers=HEADERS,
            json={
                "model": "jina-embeddings-v3",
                "input": [text],
                "task": "retrieval.query"
            }
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"🧬 Embedding Error: {e}")
        return None

def rerank_content(query: str, documents: List[str]) -> List[Dict]:
    """Rerank documents based on relevance to query"""
    try:
        response = requests.post(
            "https://api.jina.ai/v1/rerank",
            headers=HEADERS,
            json={
                "model": "jina-reranker-v2-base-multilingual",
                "query": query,
                "documents": documents
            }
        )
        response.raise_for_status()
        return response.json()["results"]
    except Exception as e:
        print(f"🔬 Reranker Error: {e}")
        return []

def segment_content(content: str) -> Dict:
    """Segment content into chunks using Segmenter API"""
    try:
        response = requests.post(
            "https://segment.jina.ai/",
            headers=HEADERS,
            json={"content": content, "return_chunks": True}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✂️ Segmenter Error: {e}")
        return {"chunks": []} # Return empty chunks in case of error

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors with robust error handling.
    
    Args:
        vec_a (List[float]): First vector.
        vec_b (List[float]): Second vector.
    
    Returns:
        float: Cosine similarity between 0 and 1, or 0.0 for invalid inputs.
    """
    if vec_a is None or vec_b is None:
        return 0.0
    
    try:
        # Ensure vectors have the same length
        if len(vec_a) != len(vec_b):
            return 0.0
        
        # Convert to numpy arrays with float64 for precision
        vec_a = np.array(vec_a, dtype=np.float64)
        vec_b = np.array(vec_b, dtype=np.float64)
        
        # Handle zero vectors
        if np.all(vec_a == 0) or np.all(vec_b == 0):
            return 0.0
        
        # Compute magnitudes safely
        magnitude_a = np.linalg.norm(vec_a)
        magnitude_b = np.linalg.norm(vec_b)
        
        # Prevent division by zero and handle numerical instability
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        # Compute dot product and normalize
        dot_product = np.dot(vec_a, vec_b)
        similarity = dot_product / (magnitude_a * magnitude_b)
        
        # Clamp the result between 0 and 1
        return max(0.0, min(1.0, similarity))
    
    except (TypeError, ValueError, OverflowError):
        return 0.0

def generate_report(query: str, sources: List[Dict], contents: List[Dict], analysis: List[Dict]) -> str:
    """Generate interactive terminal report with enhanced content analysis"""
    report = [f"\n🔎 Enhanced Research Report: {query}"]
    query_embedding = get_embedding(query)  # Get query embedding once

    for idx, result in enumerate(analysis[:3]):  # Top 3 sources
        source = sources[result["index"]]
        content_item = contents[result["index"]]  # This contains the timestamp
        segmented_content_response = segment_content(content_item['content'])
        content_chunks = segmented_content_response.get("chunks", [])

        relevant_chunks_text = "No relevant chunks found."
        if query_embedding and content_chunks:
            chunk_embeddings = []
            for chunk in content_chunks:
                chunk_embedding = get_embedding(chunk)
                if chunk_embedding: # Only add if embedding was successful
                    chunk_embeddings.append({'chunk': chunk, 'embedding': chunk_embedding})

            if chunk_embeddings:
                chunk_relevances = [
                    {'chunk': item['chunk'], 'relevance': cosine_similarity(query_embedding, item['embedding'])}
                    for item in chunk_embeddings
                ]
                top_chunks = sorted(chunk_relevances, key=lambda x: x['relevance'], reverse=True)[:3] # Top 3 chunks

                relevant_chunks_text = "\n    ".join([f"> {chunk['chunk']} (Relevance: {chunk['relevance']*100:.2f}%)" for chunk in top_chunks])
            else:
                relevant_chunks_text = "No relevant chunks found due to embedding issues."

        report.append(f"""
📌 Source {idx+1} - Relevance: {result['relevance_score']*100:.2f}%
   URL: {source['url']}
   Freshness: {datetime.fromisoformat(content_item['timestamp']).strftime('%Y-%m-%d %H:%M')}  # Fixed line
   Links: {len(content_item.get('links', {}))} verified
   Images: {len(content_item.get('images', {}))} found
   Top Relevant Content Chunks:
    {relevant_chunks_text}
    """)
    return "\n".join(report)

@llm.hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("query")
    @click.option("--output", type=click.Path(), help="Save results to JSON file")
    @click.option("--days", type=int, help="Limit results to last N days")
    @click.option("--site", type=str, help="Limit search to a specific site (domain)")
    def research(query: str, output: str, days: Optional[int], site: Optional[str]):
        """Perform comprehensive research using Jina AI APIs"""
        db = sqlite_utils.Database(logs_db_path())

        print("\n🛠️ Jina Research Pipeline (Improved):")
        print("1. 🌐 Searching...")
        sources = jina_search(query, site=site, days=days)

        print("2. 📥 Fetching content in parallel...")
        contents = []
        with ThreadPoolExecutor(max_workers=5) as executor: # Parallel processing
            futures = [executor.submit(process_url, source["url"]) for source in sources]
            for future in as_completed(futures):
                contents.append(future.result())

        print("3. ✂️ Segmenting and Analyzing Content...")
        analysis = rerank_content(query, [c["content"] for c in contents if c])

        print("4. 📊 Generating enhanced report...")
        report = generate_report(query, sources, contents, analysis)

        # Log the research session
        db["research_logs"].insert({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": len(sources),
            "results": len(analysis),
            "report": report
        })

        print(report)
        print("\n✅ Research complete! Visit Jina AI for more tools: https://jina.ai")

        if output:
            with open(output, "w") as f:
                json.dump({
                    "query": query,
                    "sources": sources,
                    "contents": contents,
                    "analysis": analysis
                }, f, indent=2)
            print(f"\n📄 Results saved to {output}")

@llm.hookimpl
def register_models(register):
    pass

@llm.hookimpl
def register_prompts(register):
    pass
