import asyncio
import os
import sys

# Import search and RAG modules directly
import search
import rag

# Configure environment


async def main():

    # Get query from command line or input
    # if len(sys.argv) > 1:
    #     query = " ".join(sys.argv[1:])
    # else:
    #     query = input("Enter search query: ")
    # Directly assign the desired query
    query = "based on warren buffett annual shareholder meeting 2025, what investment advices do we get for common people?"

    print(f"Searching for: {query}")

    try:
        # Call search directly (now uses Tavily)
        # raw_results is List[Dict[str, Any]]
        formatted_results, raw_results = await search.search_web(query)

        if not raw_results:
            print("No search results found.")
            return

        print(f"Found {len(raw_results)} search results")

        # --- Updated Logic ---
        # Check if there are results with content to pass to RAG
        # No need to extract URLs separately anymore if rag.create_rag uses raw_results
        # urls = [result.get('url') for result in raw_results if result.get('url')] # Old URL extraction (not needed for rag.create_rag)
        # if not urls: # Check based on raw_results instead
        #     print("No valid URLs found in search results.") # Message might be misleading now
        #     return

        # Check if raw_results actually contain content suitable for RAG
        docs_for_rag = [res for res in raw_results if res.get('content')]
        if not docs_for_rag:
             print("No search results with content found to process for RAG.")
             # Optionally print formatted_results here anyway if desired
             print("\n=== Search Results (Formatted) ===")
             print(formatted_results)
             return

        print(f"Processing {len(docs_for_rag)} results with content for RAG")

        # Create RAG using the raw_results list directly
        # vectorstore = await rag.create_rag(urls) # Old call
        vectorstore = await rag.create_rag(docs_for_rag) # Pass the list of dictionaries with content

        # Handle potential failure in vectorstore creation (e.g., if rag.create_rag returns None)
        if vectorstore is None:
            print("Failed to create RAG vector store (likely no documents processed).")
            # Optionally print formatted_results here as well
            print("\n=== Search Results (Formatted) ===")
            print(formatted_results)
            return

        rag_results = await rag.search_rag(query, vectorstore)

        # Format results
        print("\n=== Search Results (Formatted) ===")
        print(formatted_results) # Display the formatted Tavily results

        print("\n=== RAG Results (from Vector Store Search) ===")
        if rag_results:
            for doc in rag_results:
                # Include source if available in metadata
                source = doc.metadata.get('source', 'Unknown Source')
                print(f"\n---\nSource: {source}\nContent: {doc.page_content}")
        else:
            print("No relevant results found in the vector store for the query.")

    except Exception as e:
        print(f"An error occurred: {e}") # Changed error message slightly
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())