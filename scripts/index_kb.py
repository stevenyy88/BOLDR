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

from app.kb.indexer import KBIndexer


def main():
    parser = argparse.ArgumentParser(description="Index BOLDR Knowledge Base into ChromaDB")
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).parent.parent.parent / "dataset"),
        help="Path to dataset directory",
    )
    parser.add_argument("--chroma-host", default="localhost", help="ChromaDB host")
    parser.add_argument("--chroma-port", type=int, default=8000, help="ChromaDB port")
    args = parser.parse_args()

    print("=" * 60)
    print("BOLDR Knowledge Base Indexer")
    print("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP")
    print("=" * 60)

    indexer = KBIndexer(data_dir=args.data_dir)

    # Index all documents
    print("\n📚 Indexing all KB documents...")
    documents = indexer.index_all()

    print(f"\n✅ Indexed {len(documents)} document chunks")
    print(f"   Source distribution:")
    from collections import Counter
    sources = Counter(d["source_file"] for d in documents)
    for source, count in sources.most_common():
        print(f"     {source}: {count} chunks")

    print(f"\n🎯 Categories:")
    categories = Counter(d.get("category", "unknown") for d in documents)
    for cat, count in categories.most_common():
        print(f"     {cat}: {count} chunks")

    print("\n✅ Knowledge Base indexing complete!")
    print("   Start ChromaDB: docker compose up chromadb")
    print("   Query via: http://localhost:8000")


if __name__ == "__main__":
    main()