# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.

"""
`chATLAS_Embed/VectorStoreCreators.py`

A collection of different VectorStoreCreators

IMPLEMENTATIONS HERE:
TWikiHTMLVectorStoreCreator - Creates a Twiki vectorstore from HTML Files
TWikiTextVectorStoreCreator - Creates a Twiki vectorstore from TEXT Files

CDSTextVectorStoreCreator - Creates CDS vectorstore from CDS TEXT files
"""
from bs4 import BeautifulSoup

from .TwikiProcessors import *
from .Base import *
from tqdm import tqdm


# ---- VECTORSTORE FROM HTML TWIKI DOCUMENTS ----
class TWikiHTMLVectorStoreCreator(BaseVectorStoreCreator):
    """
    VectorStore creator for Twiki documents from HTML files
    """

    def process_document(self, html_content: str) -> Document:
        """
        Process a document from string into standard Document format

        :param html_content: (str) - string of preprocessed HTML content

        :return:
        Document of HTML data
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract TWiki metadata
        title = soup.find('title').text if soup.find('title') else ''
        url = soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else ''

        # Process page_content
        content = self._extract_content(soup)

        return Document(
            page_content=content,
            metadata={
                'title': title,
                'url': url,
                'type': 'twiki'
            },
            id=self._generate_id(url)
        )

    def load_documents(self, input_path: Path) -> List[str]:
        """
        Load HTML documents from directory in `input_path`

        :param input_path: (Path) - Path to directory containing HTML files
        """
        html_files = []
        for file_path in input_path.glob('**/*.html'):
            with open(file_path, 'r', encoding='utf-8') as f:
                html_files.append(f.read())
        return html_files

    def _extract_content(self, soup: BeautifulSoup) -> str:
        # Extract and clean page_content
        main_content = soup.find('div', {'class': 'twikiMain'})
        if main_content:
            # Remove unwanted elements
            for element in main_content.find_all(['script', 'style']):
                element.decompose()
            return main_content.get_text(separator=' ', strip=True)
        return ''

    def _generate_id(self, url: str) -> str:
        return url.split('/')[-1]


# ---- VECTORSTORE FROM TEXT TWIKI DOCUMENTS ----
class TWikiTextVectorStoreCreator(BaseVectorStoreCreator):
    """Vector store creator for TWiki text files."""

    def process_document(self, twiki_doc: TWikiTextDocument) -> Document:
        """
        Process TWiki text document into Document format.
        :param twiki_doc: (TWikiTextDocument) - Preprocessed text file into TwikiTextDocument format

        :return:
        Document containing text content
        """
        return Document(
            page_content=twiki_doc.content,
            metadata={
                'type': 'twiki',
                'name': twiki_doc.name,
                'url': twiki_doc.url,
                'parent_structure': twiki_doc.parent_structure,
                'last_modification': twiki_doc.last_modification,
                'html_file_path': twiki_doc.html_path
            },
            id=twiki_doc.name
        )

    def load_documents(self, input_path: Path) -> List[TWikiTextDocument]:
        """
        Load TWiki documents from text files contained in directory `input_path`.

        :param input_path: (Path) - Path to directory containing .txt files
        """
        processor = TWikiTextProcessor()
        documents = []

        for file_path in tqdm(input_path.glob('**/*.txt')):
            if file_path.stem == 'processed':
                continue
            try:
                doc = processor.read_twiki_text(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return documents


class CDSTextVectorStoreCreator(BaseVectorStoreCreator):
    """
    Class to load and process CDS docs into standard document form to be added to DB
    """

    def load_documents(self, input_path: Path) -> List[Any]:

        """
        Load CDS docs from path into Document form
        Currently set up to use CDS docs in `/eos/atlas/atlascerngroupdisk/phys-mlf/Chatlas/Database/Scraping/CDS`
        but should theoretically work wherever the docs are stored as latex.txt files and with meta_info.txt files
        """
        # Initialize a list to store the file paths

        documents = []
        for file_path in input_path.rglob('latex.txt'):
            # Get metadata
            with open(file_path.parent / "meta_info.txt", 'r', encoding='utf-8') as f:
                try:
                    for line in f:
                        if line.startswith("PAPER NAME :"):
                            paperName = line.split(":", 1)[1].strip()
                        elif line.startswith("LAST MODIFICATION DATE :"):
                            lastModification = line.split(":", 1)[1].strip()
                        elif line.startswith("URL :"):
                            url = line.split(":", 1)[1].strip()
                except Exception as e:
                    print(f"Error processing document {file_path.parent} - Error: {e}")
                    continue
            # Get CDS doc page_content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            doc = Document(
                page_content=content,
                metadata={
                    'type': 'CDS',
                    'name': paperName,
                    'url': url,
                    'last_modification': lastModification,
                },
                id=paperName
            )
            documents.append(doc)

        return documents

    def process_document(self, document: Any) -> Document:
        """Already in Document dataclass format on input so can just return"""
        return document
