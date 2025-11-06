# embedding_manager.py = manages the embedding lifecycle for EchoPal by extracting text from PDFs, converting it into vector embeddings using a
# SentenceTransformer, storing and searching them in a persistent ChromaDB database, and allowing document removal from the vector store.
# Augmented part from RAG

import os
import pdfplumber
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self):
        # Define absolute persistence path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        persist_path = os.path.join(base_dir, "vector_store")

        # Load local embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Initialize persistent ChromaDB storage with ABSOLUTE path
        # self.client = chromadb.Client(Settings(persist_directory=persist_path))
        self.client = chromadb.PersistentClient(path=persist_path)

        # Create or get collection
        self.collection = self.client.get_or_create_collection(name="echopal_policies")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    def chunk_text(self, text, chunk_size=600):
        """Split text into manageable chunks"""
        words = text.split()
        return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    # to prevent duplicate embedding
    def is_pdf_indexed(self, pdf_name):
        items = self.collection.get(include=["metadatas"])
        for meta in items["metadatas"]:
            if meta.get("source") == pdf_name:
                return True
        return False

    def add_pdf_to_collection(self, pdf_path):
        """Extract text, embed, and store in Chroma"""
        pdf_name = os.path.basename(pdf_path)

        # Skip if already indexed
        if self.is_pdf_indexed(pdf_name):
            return  # just skip silently

        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)

        # Generate local embeddings
        embeddings = self.model.encode(chunks, convert_to_numpy=True).tolist()

        # Store in Chroma
        self.collection.add(
            documents=chunks,
            metadatas=[{"source": pdf_name}] * len(chunks),
            ids=[f"{pdf_name}_{i}" for i in range(len(chunks))]
        )
        print(f"✅ Added {len(chunks)} chunks from {pdf_name} to vector DB.")
        return {"status": "added", "pdf": pdf_name, "chunks": len(chunks)}

    def search(self, query, top_k: int =8):
        """Search most relevant chunks and return (doc, source, distance) tuples."""
        # ask Chroma for documents, metadatas and distances
        print("🧠 Inside search(), running query for:", query)
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # # ✅ Check if embeddings are actually stored
        print("Number of embeddings in collection:",
              len(self.collection.get(include=["embeddings"])["embeddings"]))

        # Normalize length safety
        tuples = []
        for d, m, dist in zip(docs, metadatas, distances):
            src = m.get("source") if isinstance(m, dict) else m
            tuples.append((d, src, dist))

        return tuples

        # """Search most relevant chunks"""
        # results = self.collection.query(
        #     query_texts=[query],
        #     n_results=top_k
        # )
        # docs = results.get("documents", [[]])[0]
        # sources = results.get("metadatas", [[]])[0]
        # return list(zip(docs, [s["source"] for s in sources]))

    def remove_pdf_from_collection(self, pdf_name):
        """Remove all chunks of a specific PDF from the vector DB and refresh collection"""
        print(f"🧹 Attempting to remove {pdf_name} from vector store...")

        # Get all metadatas and ids
        all_items = self.collection.get(include=["metadatas"])
        all_metadatas = all_items["metadatas"]
        all_ids = all_items["ids"]

        # Match IDs by source metadata
        ids_to_delete = [
            doc_id for doc_id, meta in zip(all_ids, all_metadatas)
            if meta.get("source") == pdf_name
        ]

        if not ids_to_delete:
            print(f"⚠️ No embeddings found for {pdf_name}.")
            return {"status": "not_found", "pdf": pdf_name}

        # Delete matched embeddings
        self.collection.delete(ids=ids_to_delete)
        print(f"🗑️ Removed {len(ids_to_delete)} chunks of {pdf_name} from vector DB.")

        # ✅ Optional: compact database to free space and prevent ghost embeddings
        try:
            self.client.persist()
            print("💾 ChromaDB persisted after cleanup.")
        except Exception as e:
            print(f"⚠️ Persist error (safe to ignore): {e}")

        return {"status": "removed", "pdf": pdf_name, "deleted_chunks": len(ids_to_delete)}

        # """Remove all chunks of a specific PDF from the vector DB"""
        # # Get all documents and metadatas
        # all_items = self.collection.get(include=["documents", "metadatas"])
        # all_docs = all_items["documents"]
        # all_metadatas = all_items["metadatas"]
        #
        # # Reconstruct IDs based on how they were added
        # all_ids = []
        # for doc_idx, meta in enumerate(all_metadatas):
        #     if meta.get("source") == pdf_name:
        #         all_ids.append(f"{pdf_name}_{doc_idx}")
        #
        # if not all_ids:
        #     print(f"⚠️ No entries found for {pdf_name}.")
        #     return
        #
        # # Delete the selected chunks
        # self.collection.delete(ids=all_ids)
        # print(f"🗑️ Removed {len(all_ids)} chunks from {pdf_name} in vector DB.")