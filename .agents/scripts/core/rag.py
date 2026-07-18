import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple

class Document:
    def __init__(self, doc_id: str, content: str, source_file: str):
        self.doc_id = doc_id
        self.content = content
        self.source_file = source_file
        self.tf: Dict[str, float] = {}

class RAGIndexer:
    """A lightweight, dependency-free TF-IDF semantic search indexer."""
    
    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.documents: Dict[str, Document] = {}
        self.idf: Dict[str, float] = {}
        self.vocab = set()
        
    def _tokenize(self, text: str) -> List[str]:
        # Simple tokenizer: lowercase, extract alphanumeric words > 2 chars
        return [word for word in re.findall(r'\b\w+\b', text.lower()) if not word.isdigit() and len(word) > 2]
        
    def add_document(self, doc_id: str, content: str, source_file: str):
        doc = Document(doc_id, content, source_file)
        tokens = self._tokenize(content)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return
            
        counter = Counter(tokens)
        for word, count in counter.items():
            doc.tf[word] = count / total_tokens
            self.vocab.add(word)
            
        self.documents[doc_id] = doc
        
    def compute_idf(self):
        total_docs = len(self.documents)
        self.idf.clear()
        
        for word in self.vocab:
            doc_count = sum(1 for doc in self.documents.values() if word in doc.tf)
            self.idf[word] = math.log((total_docs + 1) / (doc_count + 1)) + 1
            
    def save(self):
        data = {
            "idf": self.idf,
            "documents": {
                doc_id: {
                    "content": doc.content,
                    "source_file": doc.source_file,
                    "tf": doc.tf
                }
                for doc_id, doc in self.documents.items()
            }
        }
        self.index_file.write_text(json.dumps(data, indent=2))
        
    def load(self):
        if not self.index_file.exists():
            return
        try:
            data = json.loads(self.index_file.read_text())
        except json.JSONDecodeError:
            return
            
        self.idf = data.get("idf", {})
        self.documents = {}
        for doc_id, doc_data in data.get("documents", {}).items():
            doc = Document(doc_id, doc_data["content"], doc_data["source_file"])
            doc.tf = doc_data["tf"]
            self.documents[doc_id] = doc
            
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        query_tokens = self._tokenize(query)
        query_counter = Counter(query_tokens)
        
        scores = []
        for doc in self.documents.values():
            score = 0.0
            for word, q_count in query_counter.items():
                if word in doc.tf and word in self.idf:
                    q_tfidf = q_count * self.idf[word]
                    d_tfidf = doc.tf[word] * self.idf[word]
                    score += q_tfidf * d_tfidf
            if score > 0:
                scores.append((doc, score))
                
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

def chunk_markdown(content: str) -> List[str]:
    """Splits markdown content into semantic chunks based on headers."""
    chunks = re.split(r'\n##+ ', content)
    result = [chunks[0]] if chunks[0].strip() else []
    for chunk in chunks[1:]:
        result.append("## " + chunk)
    return [c.strip() for c in result if c.strip()]

def chunk_yaml(content: str) -> List[str]:
    """Splits YAML lists into semantic chunks."""
    chunks = re.split(r'\n- ', content)
    result = [chunks[0]] if chunks[0].strip() else []
    for chunk in chunks[1:]:
        result.append("- " + chunk)
    return [c.strip() for c in result if c.strip()]

def index_memory_files(project_root: Path):
    """Indexes memory files into a lightweight RAG store."""
    index_path = project_root / ".agents" / ".rag_index.json"
    indexer = RAGIndexer(index_path)
    
    # Index lessons learned
    lessons_path = project_root / ".agents" / "memory" / "lessons-learned.yaml"
    if lessons_path.exists():
        content = lessons_path.read_text()
        chunks = chunk_yaml(content)
        for i, chunk in enumerate(chunks):
            indexer.add_document(f"lesson_{i}", chunk, "lessons-learned.yaml")
            
    # Index schema
    schema_path = project_root / ".agents" / "schema.md"
    if schema_path.exists():
        content = schema_path.read_text()
        chunks = chunk_markdown(content)
        for i, chunk in enumerate(chunks):
            indexer.add_document(f"schema_{i}", chunk, "schema.md")
            
    indexer.compute_idf()
    indexer.save()
    return indexer
