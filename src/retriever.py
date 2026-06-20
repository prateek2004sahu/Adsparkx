import os
import json
import math
import re
from pathlib import Path
from typing import List, Dict, Tuple
import anthropic

# We use simple TF-IDF style retrieval + Claude embeddings simulation via keyword scoring
# For production use ChromaDB / FAISS with real embeddings

DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_FILE = Path(__file__).parent.parent / "vector_store.json"

def load_documents() -> List[Dict]:
    """Load all documents from the data directory."""
    docs = []
    supported = {".txt", ".md", ".json"}
    
    for filepath in DATA_DIR.glob("**/*"):
        if filepath.suffix.lower() in supported and filepath.is_file():
            try:
                text = filepath.read_text(encoding="utf-8")
                docs.append({
                    "source": filepath.name,
                    "path": str(filepath),
                    "content": text,
                    "type": filepath.suffix.lstrip(".")
                })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
    
    return docs

def chunk_document(doc: Dict, chunk_size: int = 400, overlap: int = 80) -> List[Dict]:
    """Split document into overlapping chunks."""
    text = doc["content"]
    words = text.split()
    chunks = []
    
    i = 0
    chunk_idx = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Try to detect section heading
        lines = chunk_text.split("\n")
        section = ""
        for line in lines[:3]:
            line = line.strip()
            if line.startswith("#") or (len(line) < 60 and line.isupper()):
                section = line.lstrip("#").strip()
                break
        
        chunks.append({
            "id": f"{doc['source']}::chunk_{chunk_idx}",
            "source": doc["source"],
            "section": section or f"Section {chunk_idx + 1}",
            "text": chunk_text,
            "word_count": len(chunk_words)
        })
        i += chunk_size - overlap
        chunk_idx += 1
    
    return chunks

def build_tf_idf_index(chunks: List[Dict]) -> Dict:
    """Build a simple TF-IDF index for keyword-based retrieval."""
    # Compute term frequencies per chunk
    idf = {}
    N = len(chunks)
    
    for chunk in chunks:
        terms = set(tokenize(chunk["text"]))
        for term in terms:
            idf[term] = idf.get(term, 0) + 1
    
    # IDF scores
    idf_scores = {t: math.log(N / (df + 1)) for t, df in idf.items()}
    
    # TF-IDF vectors per chunk
    vectors = []
    for chunk in chunks:
        tokens = tokenize(chunk["text"])
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        total = len(tokens)
        vec = {t: (c / total) * idf_scores.get(t, 0) for t, c in tf.items()}
        vectors.append(vec)
    
    return {"idf_scores": idf_scores, "vectors": vectors, "chunks": chunks}

def tokenize(text: str) -> List[str]:
    """Simple tokenizer."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

def cosine_sim(v1: Dict, v2: Dict) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    mag1 = math.sqrt(sum(x**2 for x in v1.values()))
    mag2 = math.sqrt(sum(x**2 for x in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []

    def build(self, docs: List[Dict]):
        """Ingest docs, chunk them, build index."""
        all_chunks = []
        for doc in docs:
            chunks = chunk_document(doc)
            all_chunks.extend(chunks)
        
        self.index = build_tf_idf_index(all_chunks)
        self.chunks = all_chunks
        print(f"[RAG] Indexed {len(all_chunks)} chunks from {len(docs)} documents.")

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Retrieve top-k relevant chunks for a query."""
        if not self.index:
            return []
        
        query_tokens = tokenize(query)
        total = len(query_tokens)
        if total == 0:
            return []
        
        tf_query = {}
        for t in query_tokens:
            tf_query[t] = tf_query.get(t, 0) + 1
        
        query_vec = {
            t: (c / total) * self.index["idf_scores"].get(t, 0)
            for t, c in tf_query.items()
        }
        
        scores = []
        for i, vec in enumerate(self.index["vectors"]):
            score = cosine_sim(query_vec, vec)
            scores.append((self.chunks[i], score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
