from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# import search # No longer needed for get_web_content
from langchain_core.documents import Document
import os
import asyncio
from typing import List, Dict, Any # Added typing


# Updated function signature and logic
async def create_rag(search_results: List[Dict[str, Any]]) -> FAISS:
    """
    Create a RAG vector store from Tavily search results.

    Args:
        search_results: A list of dictionaries, where each dictionary represents a search result
                        from Tavily, expected to have 'content' and 'url'.

    Returns:
        FAISS: Vector store object.
    """
    try:
        # model_name = os.getenv("MODEL", "text-embedding-ada-002")
        # Change any embedding you want, whether Ollama or MistralAIEmbeddings
        # embeddings = MistralAIEmbeddings(
        #     model="mistral-embed",
        #     chunk_size=64
        # )
        embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        # embeddings = OpenAIEmbeddings(
        #     model=model_name,
        #     openai_api_key=os.getenv("OPENAI_API_KEY"),
        #     openai_api_base=os.getenv("OPENAI_API_BASE"),
        #     chunk_size=64
        # )

        # Create Document objects directly from Tavily results
        documents = []
        for result in search_results:
            content = result.get('content')
            url = result.get('url')
            if content and url: # Only process results with both content and URL
                documents.append(Document(page_content=content, metadata={"source": url}))
            elif content: # Handle cases where URL might be missing but content exists
                 documents.append(Document(page_content=content, metadata={"source": "Unknown (URL missing from Tavily result)"}))


        if not documents:
             print("Warning: No documents could be created from the provided search results.")
             # Return an empty FAISS index or handle as appropriate
             # Creating an empty index requires at least one dummy document/embedding
             # For simplicity, let's raise an error or return None if you prefer
             # raise ValueError("Cannot create FAISS index with no documents.")
             # Alternatively, return an empty index if the library allows:
             # return FAISS.from_texts([""], embeddings) # Check FAISS documentation for empty index creation
             # For now, let's return None or raise error, adjust as needed
             print("Returning None as no documents were available for vector store creation.")
             return None # Or raise ValueError("No documents to create vector store")


        # Text chunking processing (May need adjustment depending on Tavily content length)
        # Consider if chunking is necessary if Tavily content is already snippet-like
        text_splitter = RecursiveCharacterTextSplitter(
            # chunk_size=10000, # Adjust chunk size based on expected content length from Tavily
            # chunk_overlap=500, # Adjust overlap
            chunk_size=1000, # Example smaller chunk size suitable for snippets
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        split_documents = text_splitter.split_documents(documents)
        # print(documents)

        # Ensure embeddings are calculated before creating the index
        # (FAISS.from_documents handles this internally)
        vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
        return vectorstore
    except Exception as e:
        print(f"Error in create_rag: {str(e)}")
        # Optionally re-raise or handle the error appropriately
        raise # Re-raise the exception to signal failure

async def create_rag_from_documents(documents: list[Document]) -> FAISS:
    """
    Create a RAG system directly from a list of documents to avoid repeated web scraping
    
    Args:
        documents: List of already fetched documents
        
    Returns:
        FAISS: Vector store object
    """
    try:
        # model_name = os.getenv("MODEL")
        # embeddings = OpenAIEmbeddings(
        #     model=model_name,
        #     openai_api_key=os.getenv("OPENAI_API_KEY"),
        #     openai_api_base=os.getenv("OPENAI_API_BASE"),
        #     chunk_size=64
        # )
        embeddings = OllamaEmbeddings(model="nomic-embed-text:latest") # Ensure consistency

        # Text chunking processing
        text_splitter = RecursiveCharacterTextSplitter(
            # chunk_size=10000, # Adjust chunk size if needed
            # chunk_overlap=500,
            chunk_size=1000, # Keep consistent with create_rag
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        split_documents = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
        return vectorstore
    except Exception as e:
        print(f"Error in create_rag_from_documents: {str(e)}")
        raise

async def search_rag(query: str, vectorstore: FAISS) -> list[Document]:
    """
    Search the RAG system with a query
    
    Args:
        query: Search query string
        vectorstore: FAISS vector store to search against
        
    Returns:
        list[Document]: List of relevant documents
    """
    return vectorstore.similarity_search(query, k=3)