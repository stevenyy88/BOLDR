"""
BOLDR Self-Improving Customer Intelligence Engine
Knowledge Base Retriever — Hybrid search (vector + keyword)

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import os
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions


class KBRetriever:
    """Hybrid knowledge base retriever using ChromaDB vector search
    with keyword fallback for BOLDR product knowledge."""

    def __init__(
        self,
        chroma_host: str = None,
        chroma_port: int = None,
        collection_name: str = "boldr_kb",
        confidence_threshold: float = 0.5,
    ):
        self.chroma_host = chroma_host or os.environ.get("CHROMA_HOST", "localhost")
        self.chroma_port = chroma_port or int(os.environ.get("CHROMA_PORT", "8100"))
        self.collection_name = collection_name
        self.confidence_threshold = confidence_threshold
        self._client = None
        self._collection = None

    @property
    def client(self) -> chromadb.HttpClient:
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
            )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn,
                metadata={"description": "BOLDR Knowledge Base"},
            )
        return self._collection

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> dict:
        """Search the knowledge base using hybrid approach.

        Args:
            query: The customer question or search query.
            n_results: Number of results to return.
            filter_metadata: Optional metadata filters (e.g., source_file, section).

        Returns:
            dict with keys: results, best_match, confidence, is_answerable
        """
        # Vector search via ChromaDB
        query_params = {
            "query_texts": [query],
            "n_results": n_results,
        }
        if filter_metadata:
            query_params["where"] = filter_metadata

        try:
            results = self.collection.query(**query_params)
        except Exception as e:
            return {
                "results": [],
                "best_match": None,
                "confidence": 0.0,
                "is_answerable": False,
                "error": str(e),
            }

        if not results["ids"] or not results["ids"][0]:
            return {
                "results": [],
                "best_match": None,
                "confidence": 0.0,
                "is_answerable": False,
            }

        # Process results
        processed = []
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            content = results["documents"][0][i] if results["documents"] else ""
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 1.0

            # Convert distance to confidence (lower distance = higher confidence)
            confidence = max(0.0, 1.0 - distance)

            processed.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata,
                "distance": distance,
                "confidence": confidence,
            })

        best = processed[0] if processed else None
        best_confidence = best["confidence"] if best else 0.0

        return {
            "results": processed,
            "best_match": best,
            "confidence": best_confidence,
            "is_answerable": best_confidence >= self.confidence_threshold,
        }

    def search_by_category(
        self,
        query: str,
        category: str,
        n_results: int = 3,
    ) -> dict:
        """Search within a specific KB category.

        Categories match the BOLDR document structure:
        - 'product_specs' — product reference data
        - 'engraving' — engraving rate card
        - 'servicing' — servicing rate card
        - 'faq' — FAQ entries
        - 'sop' — CS SOP procedures
        """
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"category": category},
        )

    def get_kb_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "status": "healthy",
            }
        except Exception as e:
            return {
                "total_documents": 0,
                "collection_name": self.collection_name,
                "status": f"error: {e}",
            }


if __name__ == "__main__":
    retriever = KBRetriever()
    print("KB Retriever initialised.")
    stats = retriever.get_kb_stats()
    print(f"KB Stats: {stats}")