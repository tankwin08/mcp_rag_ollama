import asyncio
from dotenv import load_dotenv
import os
# from exa_py import Exa # No longer needed
from tavily import TavilyClient # Import Tavily client
from typing import List, Tuple, Dict, Any # Updated typing
from langchain_core.documents import Document
# from langchain_community.document_loaders.firecrawl import FireCrawlLoader # No longer needed if Tavily provides content
import requests # Keep for now, might be needed for fallback or other HTTP tasks

# Load .env variables
load_dotenv(override=True)

# Initialize the Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable not set.")
tavily = TavilyClient(api_key=tavily_api_key)
# os.environ['FIRECRAWL_API_KEY'] = os.getenv("FIRECRAWL_API_KEY") # No longer needed

# Default search config (adjust for Tavily if needed)
websearch_config = {
    "parameters": {
        "default_num_results": 5,
        "include_domains": [],
        "max_tokens": 4000 # Example Tavily parameter: max tokens for context per result
    }
}

# Constants for web content fetching (might be less relevant now)
MAX_RETRIES = 3
# FIRECRAWL_TIMEOUT = 30 # No longer needed for Firecrawl

# --- Modified search_web function ---
async def search_web(query: str, num_results: int = None) -> Tuple[str, List[Dict[str, Any]]]:
    """Search the web using Tavily API and return both formatted results and raw results (dictionaries)."""
    try:
        search_depth = "advanced" # Use advanced for potentially more content
        max_results = num_results or websearch_config["parameters"]["default_num_results"]

        # Use Tavily SDK's search method
        # include_raw_content=True can be added if needed, but increases token usage
        search_results = await asyncio.to_thread(
            tavily.search,
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=False, # We usually want the sources, not a generated answer
            include_images=False,
            # include_raw_content=True, # Optionally get raw HTML - increases cost/tokens
        )
        # The Tavily SDK returns a dictionary, often with a 'results' key containing a list of dictionaries
        raw_results_list = search_results.get('results', [])
        formatted_results = format_tavily_search_results(raw_results_list)

        # Return the formatted string and the list of result dictionaries
        return formatted_results, raw_results_list
    except Exception as e:
        print(f"An error occurred while searching with Tavily: {e}") # Added print statement
        # Consider more specific error handling based on Tavily exceptions if needed
        return f"An error occurred while searching with Tavily: {e}", []

# --- New function to format Tavily results ---
def format_tavily_search_results(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "No results found."

    markdown_results = "### Search Results (Tavily):\n\n"
    for idx, result in enumerate(results, 1):
        title = result.get('title', "No title")
        url = result.get('url', "#")
        # Tavily provides 'content', which is often a summary or key points
        content_snippet = result.get('content', "No content snippet available.")
        score = result.get('score', None)
        score_str = f" (Score: {score:.2f})" if score is not None else ""

        markdown_results += f"**{idx}.** [{title}]({url}){score_str}\n"
        markdown_results += f"> **Content:** {content_snippet}\n\n" # Display the content Tavily returned

    return markdown_results

# --- get_web_content function (Potentially Obsolete) ---
async def get_web_content(url: str) -> List[Document]:
    """
    Get web content. NOTE: This might be unnecessary if Tavily provides enough content.
    If needed, replace Firecrawl with a different scraper (e.g., WebBaseLoader or BeautifulSoup).
    """
    print(f"Warning: get_web_content called for {url}. Consider using content directly from Tavily search results.")
    # If you STILL need full page scraping, implement it here using a different library:
    # Example using WebBaseLoader (requires pip install langchain-community beautifulsoup4)
    # from langchain_community.document_loaders import WebBaseLoader
    # try:
    #     loader = WebBaseLoader(web_path=url, continue_on_failure=True)
    #     loader.requests_per_second = 2 # Be polite
    #     loader.requests_kwargs = {'timeout': 15}
    #     documents = await loader.aload()
    #     if documents and documents[0].page_content: # Check if content was actually loaded
    #          return documents
    #     else:
    #          print(f"WebBaseLoader failed to get content for {url}")
    #          # Return a minimal document indicating failure
    #          return [Document(page_content=f"Failed to retrieve content from {url}", metadata={"source": url, "error": "Scraping failed"})]
    # except Exception as e:
    #     print(f"Error using WebBaseLoader for {url}: {e}")
    #     return [Document(page_content=f"Error retrieving content from {url}: {e}", metadata={"source": url, "error": str(e)})]

    # Placeholder if you remove scraping entirely for now:
    return [Document(page_content=f"Scraping function (get_web_content) needs implementation or removal if Tavily content is sufficient. URL: {url}", metadata={"source": url, "warning": "Scraping not performed"})]

async def get_web_content(url: str) -> List[Document]:
    """Get web content and convert to document list."""
    for attempt in range(MAX_RETRIES):
        try:
            # Create FireCrawlLoader instance
            loader = FireCrawlLoader(
                url=url,
                mode="scrape"
            )
            
            # Use timeout protection
            documents = await asyncio.wait_for(loader.aload(), timeout=FIRECRAWL_TIMEOUT)
            
            # Return results if documents retrieved successfully
            if documents and len(documents) > 0:
                return documents
            
            # Retry if no documents but no exception
            print(f"No documents retrieved from {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)  # Wait 1 second before retrying
                continue
                
        except requests.exceptions.HTTPError as e:
            if "Website Not Supported" in str(e):
                # Create a minimal document with error info
                print(f"Website not supported by FireCrawl: {url}")
                content = f"Content from {url} could not be retrieved: Website not supported by FireCrawl API."
                return [Document(page_content=content, metadata={"source": url, "error": "Website not supported"})]
            else:
                print(f"HTTP error retrieving content from {url}: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
                
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)
                continue
            raise
        except Exception as e:
            print(f"Error retrieving content from {url}: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)
                continue
            raise
    
    # Return empty list if all retries failed
    return []