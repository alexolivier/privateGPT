from constants import CHROMA_SETTINGS
from langchain.docstore.document import Document
from langchain.embeddings import LlamaCppEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PDFMinerLoader, CSVLoader, SitemapLoader

import os
import glob
import nest_asyncio
from typing import List
from dotenv import load_dotenv


nest_asyncio.apply()


load_dotenv()


def load_single_document(file_path: str) -> Document:
    # Loads a single document from a file path
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf8")
    elif file_path.endswith(".adoc"):
        loader = TextLoader(file_path, encoding="utf8")
    elif file_path.endswith(".pdf"):
        loader = PDFMinerLoader(file_path)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
    return loader.load()[0]


def load_documents(source_dir: str) -> List[Document]:
    # Loads all documents from source documents directory
    # txt_files = glob.glob(os.path.join(source_dir, "**/*.txt"), recursive=True)
    # pdf_files = glob.glob(os.path.join(source_dir, "**/*.pdf"), recursive=True)
    # csv_files = glob.glob(os.path.join(source_dir, "**/*.csv"), recursive=True)
    # adoc_files = glob.glob(os.path.join(
    #     source_dir, "**/*.adoc"), recursive=True)
    # all_files = txt_files + pdf_files + csv_files + adoc_files
    # return [load_single_document(file_path) for file_path in all_files]
    loader = SitemapLoader(
        "https://docs.cerbos.dev/sitemap.xml",
        filter_urls=["https://docs.cerbos.dev/cerbos/latest/policies/"]
    )
    return loader.load()


def main():
    # Load environment variables
    persist_directory = os.environ.get('PERSIST_DIRECTORY')
    source_directory = os.environ.get('SOURCE_DIRECTORY', 'source_documents')
    llama_embeddings_model = os.environ.get('LLAMA_EMBEDDINGS_MODEL')
    model_n_ctx = os.environ.get('MODEL_N_CTX')

    # Load documents and split in chunks
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"Loaded {len(documents)} documents from {source_directory}")
    print(f"Split into {len(texts)} chunks of text (max. 500 tokens each)")

    # Create embeddings
    llama = LlamaCppEmbeddings(
        model_path=llama_embeddings_model, n_ctx=model_n_ctx)

    # Create and store locally vectorstore
    db = Chroma.from_documents(
        texts, llama, persist_directory=persist_directory, client_settings=CHROMA_SETTINGS)
    db.persist()
    db = None


if __name__ == "__main__":
    main()
