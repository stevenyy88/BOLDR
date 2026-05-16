#!/usr/bin/env python3
"""
BOLDR Self-Improving Customer Intelligence Engine
Knowledge Base Indexing Script

Indexes all 6 data files into ChromaDB for hybrid retrieval.

Usage:
    python scripts/index_kb.py [--data-dir PATH] [--chroma-host HOST] [--chroma-port PORT]

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import os
import chromadb
from chromadb.utils import embedding_functions
from app.kb.indexer import KBIndexer


def main():
    parser = argparse.ArgumentParser(description="Index BOLDR Knowledge Base into ChromaDB")
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("KB_DATA_DIR", str(Path(__file__).parent.parent.parent / "dataset")),
        help="Path to dataset directory",
    )
    parser.add_argument("--chroma-host", default=os.environ.get("CHROMA_HOST", "localhost"), help="ChromaDB host")
    parser.add_argument("--chroma-port", type=int, default=int(os.environ.get("CHROMA_PORT", "8100")), help="ChromaDB port")
    args = parser.parse_args()

    print("=" * 60)
    print("BOLDR Knowledge Base Indexer")
    print("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP")
    print("=" * 60)

    indexer = KBIndexer(data_dir=args.data_dir)

    # Index all documents
    print("\n📚 Indexing all KB documents...")
    documents = indexer.index_all()

    print(f"\n✅ Parsed {len(documents)} document chunks")

    # Connect to ChromaDB and insert
    print(f"\n🔌 Connecting to ChromaDB at {args.chroma_host}:{args.chroma_port}...")
    client = chromadb.HttpClient(host=args.chroma_host, port=args.chroma_port)

    # Use sentence-transformers for embeddings
    print("📦 Loading embedding model (all-MiniLM-L6-v2)...")
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create or reset the collection
    try:
        client.delete_collection("boldr_kb")
        print("   Cleared existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name="boldr_kb",
        embedding_function=embedding_fn,
        metadata={"description": "BOLDR Knowledge Base"},
    )
    print(f"   Created collection 'boldr_kb'")

    # Insert documents in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        ids = [doc["id"] for doc in batch]
        contents = [doc["content"] for doc in batch]
        metadatas = []
        for doc in batch:
            meta = doc.get("metadata", {})
            if not isinstance(meta, dict):
                meta = {}
            meta["source_file"] = doc.get("source_file", "")
            meta["section"] = doc.get("section", "")
            meta["category"] = doc.get("category", "")
            metadatas.append(meta)

        collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
        )
        print(f"   Inserted batch {i // batch_size + 1}: {len(batch)} documents")

    # Verify
    count = collection.count()
    print(f"\n✅ ChromaDB collection 'boldr_kb' now has {count} documents")

    # Print source distribution
    from collections import Counter
    sources = Counter(d["source_file"] for d in documents)
    print(f"\n📊 Source distribution:")
    for source, count_item in sources.most_common():
        print(f"     {source}: {count_item} chunks")

    categories = Counter(d.get("category", "unknown") for d in documents)
    print(f"\n🎯 Categories:")
    for cat, count_item in categories.most_common():
        print(f"     {cat}: {count_item} chunks")

    print("\n✅ Knowledge Base indexing complete!")
    print(f"   Start ChromaDB: docker compose up chromadb")
    print(f"   Query via: http://{args.chroma_host}:{args.chroma_port}")


if __name__ == "__main__":
    main()