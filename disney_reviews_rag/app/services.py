import os
import pandas as pd
from dotenv import load_dotenv
import logging

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    

logger = logging.getLogger("\t  " + __name__.strip())

def row_to_doc(row: pd.Series) -> Document:
    """
    Converts a pandas Series (row) to a LangChain Document.
    args:
        row (pd.Series): A row from a pandas DataFrame.
    returns:
        Document: A LangChain Document with content and metadata.
    """
    text = ". ".join(f"{k}: {v}" for k, v in row.items() if pd.notna(v)) + "."
    return Document(
        page_content=text,
        metadata={
            "park": row.get("park") or row.get("Park") or None,
            "country": row.get("Reviewer_Location") or row.get("country") or None,
            "rating": row.get("Rating") or row.get("rating") or None,
            "date": row.get("Date") or None,
        },
    )

def setup_qa_chain(is_local: bool = True,
                   limit_docs: int = 1000) -> RetrievalQA:
    """
    Sets up the QA chain for document retrieval.

    Args:
        is_local (bool): If True, uses local Ollama models.
                         If False, uses OpenAI models.  Default is True.
        limit_docs (int): Limits the number of documents to process when is_local is True.
    Returns:
        RetrievalQA: A LangChain RetrievalQA chain.
    Note:
        Ensure the CSV_PATH environment variable is set to the path of the CSV file.
    """
    load_dotenv()

    try:
        TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.0))
        MAX_TOKENS = int(os.environ.get("MAX_TOKENS", 500))
        CSV_PATH = os.environ.get("CSV_PATH")
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing environment variables: {e}")
        return None

    # Load data
    logger.info("Loading reviews from CSV file.")
    try:
        df = pd.read_csv(CSV_PATH, encoding="latin1")
    except FileNotFoundError:
        logger.error(f"The file '{CSV_PATH}' was not found.")
        return None
    logger.info("Reviews CSV loaded successfully.")
    
    # Chunk data
    logger.info("Creating document chunks from reviews.")
    docs = [row_to_doc(r) for _, r in df.iterrows()]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    
    if is_local:
        # Limit documents for local testing
        docs = docs[:limit_docs]
    chunks = splitter.split_documents(docs)
    logger.info(f"Created {len(chunks)} chunks from {len(docs)} documents.")

    # Set Embedding Model
    logger.info("Setting up embedding model.")
    if is_local:
        embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    else:
        embedding_model = OpenAIEmbeddings()
    logger.info("Embedding model set successfully.")
    
    # Embed and then vector store
    logger.info("Building FAISS indexing.")
    vector_store = FAISS.from_documents(chunks, embedding_model)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    logger.info("FAISS indexing built successfully.")

    # Set LLM
    logger.info("Setting up LLM.")
    if is_local:
        MODEL_NAME = os.environ.get("MODEL_NAME_LOCAL", "llama3.1:8b")
        llm = OllamaLLM(model=MODEL_NAME,
                        temperature=TEMPERATURE,
                        num_predict=MAX_TOKENS)
    else:
        MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
        llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS)
    logger.info(f"LLM model '{llm.model}' set successfully.")

    # Set Q&A Chain
    logger.info("Setting up retrieval QA chain.")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )
    logger.info("Retrieval QA chain setup complete.")

    return qa_chain