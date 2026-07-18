import os
import sys
import tempfile
from pathlib import Path

import importlib.util
spec = importlib.util.spec_from_file_location('rag', os.path.abspath('.agents/scripts/core/rag.py'))
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)

RAGIndexer = rag.RAGIndexer
chunk_markdown = rag.chunk_markdown
chunk_yaml = rag.chunk_yaml

def test_chunking():
    md = "# Header\n## Section 1\nContent 1\n## Section 2\nContent 2"
    chunks = chunk_markdown(md)
    assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
    assert "Section 1" in chunks[1]
    
    yml = "- item 1\n  desc: foo\n- item 2"
    chunks = chunk_yaml(yml)
    assert len(chunks) == 2, f"Expected 2 yaml chunks, got {len(chunks)}"
    assert "item 1" in chunks[0]

def test_indexer():
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = Path(tmp) / "index.json"
        indexer = RAGIndexer(idx_path)
        indexer.add_document("doc1", "The quick brown fox", "file1.txt")
        indexer.add_document("doc2", "The lazy dog", "file1.txt")
        indexer.add_document("doc3", "A quick semantic search index", "file2.txt")
        indexer.compute_idf()
        
        # Test TF-IDF and Search
        results = indexer.search("quick search")
        assert len(results) > 0
        assert results[0][0].doc_id == "doc3" # Contains both "quick" and "search"
        
        # Test Save/Load
        indexer.save()
        assert idx_path.exists()
        
        loader = RAGIndexer(idx_path)
        loader.load()
        assert len(loader.documents) == 3
        
if __name__ == "__main__":
    test_chunking()
    test_indexer()
    print("All RAG unit tests passed!")
