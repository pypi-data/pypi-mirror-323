# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.

"""
`chATLAS_Embed/Base.py`
Script Containing Base Classes for all Embed Implementations
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy import Engine, text


@dataclass
class Document:
    """Represents a base document with its page_content and metadata."""
    page_content: str
    metadata: Dict[str, Any]
    id: str
    parent_id: Optional[str] = None


class TextSplitter(ABC):
    """Abstract base class for text splitting strategies."""

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """Split text into chunks."""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass


class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""

    vector_size: int  # Vector size output of embedding model

    @abstractmethod
    def embed(self, texts: List[str] | str, show_progress_bar: bool = None) -> List[List[float]]:
        """Generate embeddings for a list of texts or single query.
        Currently just passed document page_content in initial creation, but could also be passed metadata"""
        pass


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    # Defined Attributes
    engine: Engine
    embedding_model: EmbeddingModel

    @abstractmethod
    def add_documents(self, parent_docs: List[Document], child_docs: List[Document]) -> None:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 4, metadata_filters: dict = None, date_filter: str = None) -> List[Document]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete(self, document_ids: List[str] = None, document_name: str = None) -> None:
        """Delete documents from the store."""
        pass


class BaseVectorStoreCreator:
    """
    Base class for creating and managing vector stores.

    Currently uses a Parent-Child document retriever setup in a similar way to: https://python.langchain.com/docs/how_to/parent_document_retriever/
    """

    def __init__(
            self,
            vector_store: VectorStore,
            child_splitter: TextSplitter,
            parent_splitter: TextSplitter,
            output_dir: Path
    ):
        """
        :param vector_store: (VectorStore) - Instantiated VectorStore to add documents to
        :param child_splitter: (TextSplitter) - Child splitter to use to split parent documents into child chunks
        :param parent_splitter: (TextSplitter) - Parent splitter to split documents into chunks
        :param output_dir: (Path) - Currently unused
        """
        self.vector_store = vector_store
        self.parent_splitter = parent_splitter
        self.child_splitter = child_splitter
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def process_document(self, document: Any) -> Document:
        """Process a single document into the Document format."""
        return document

    @abstractmethod
    def load_documents(self, input_path: Path) -> List[Any]:
        """Load documents from the input path."""
        pass

    def create_update_vectorstore(self, input_path: Path, update: bool = False, verbose: bool = True) -> None:
        """
        Create vector store from documents in input path, with optional update handling for updating the vectorstore
        from files in directory where last update date is newer than what is currently stored in the vectorstore.

        :param: input_path: (Path) - Path to directory containing documents to add (in any file type)
        :param: update: (bool) - Whether to update contents of the db if newer versions of the files are contained in input_path
        :param: verbose: (bool) - Print logging of documents added or documents updated
        """
        raw_documents = self.load_documents(input_path)

        processed_docs = []
        for doc in raw_documents:
            processed_docs.append(self.process_document(doc))

        # Split document into parent and child chunks
        parent_docs = []
        child_docs = []
        new_documents = []
        updated_documents = []

        # Collect document metadata for batch query
        document_metadata = [(doc.metadata.get("name"), doc.metadata.get("url")) for doc in processed_docs]
        names, urls = zip(*document_metadata) if document_metadata else ([], [])

        # Batch query to check existing documents
        with self.vector_store.engine.connect() as conn:
            existing_docs = conn.execute(
                text("""
                    SELECT id, metadata FROM documents 
                    WHERE metadata->>'name' IN :names OR metadata->>'url' IN :urls
                """),
                {"names": names, "urls": urls}
            ).fetchall()

            # Map existing documents by name and URL
            existing_docs_map = {doc.metadata.get("name"): doc for doc in existing_docs}

            # Process documents in parallel
            def process_document(doc):
                name = doc.metadata.get("name")
                url = doc.metadata.get("url")
                last_modified = doc.metadata.get("last_modification")

                existing_doc = existing_docs_map.get(name) or existing_docs_map.get(url)
                if existing_doc:
                    existing_metadata = existing_doc.metadata
                    existing_last_modified = existing_metadata.get("last_modification")

                    if update and last_modified and (
                            not existing_last_modified or last_modified > existing_last_modified
                    ):
                        # Update: Remove old chunks
                        conn.execute(
                            text("""
                                DELETE FROM documents 
                                WHERE metadata->>'name' = :name OR metadata->>'url' = :url
                            """),
                            {"name": name, "url": url}
                        )
                        updated_documents.append(name)
                    else:
                        # Skip if no update is required
                        return None, None
                else:
                    # New document
                    new_documents.append(name)

                parent_chunks = self.parent_splitter.split(doc.page_content)
                parent_docs_local = []
                child_docs_local = []

                for i, parent_chunk in enumerate(parent_chunks):
                    parent_id = f"{doc.id}_parent_{i}"
                    parent_doc = Document(
                        page_content=parent_chunk,
                        metadata={**doc.metadata, 'parent_index': i},
                        id=parent_id
                    )
                    parent_docs_local.append(parent_doc)

                    child_chunks = self.child_splitter.split(parent_chunk)
                    for j, child_chunk in enumerate(child_chunks):
                        child_id = f"{parent_id}_child_{j}"
                        child_doc = Document(
                            page_content=child_chunk,
                            metadata={
                                **parent_doc.metadata,
                                'chunk_index': j,
                                'parent_content_length': len(parent_chunk),
                                'child_content_length': len(child_chunk)
                            },
                            id=child_id,
                            parent_id=parent_id
                        )
                        child_docs_local.append(child_doc)

                return parent_docs_local, child_docs_local

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(process_document, processed_docs))

            # Aggregate results
            for parent_docs_local, child_docs_local in results:
                if parent_docs_local and child_docs_local:
                    parent_docs.extend(parent_docs_local)
                    child_docs.extend(child_docs_local)

        # Add documents to the vector store
        if parent_docs and child_docs:
            self.vector_store.add_documents(parent_docs, child_docs)

        # Log results
        if verbose:
            print(f"New documents added: {len(new_documents)} - {new_documents}")
            print(f"Documents updated: {len(updated_documents)} - {updated_documents}")


