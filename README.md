
# MCP RAG Ollama Project

This project demonstrates a Retrieval Augmented Generation (RAG) system using Langchain, the MCP framework (likely `FastMCP`), and local Large Language Models (LLMs) served via Ollama. It allows for web searching, content processing, and querying an AI agent backed by local models.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python**: Version 3.10 or higher.
- **Ollama**: Follow the installation guide at [https://ollama.com/](https://ollama.com/).
- **uv**: A fast Python package installer and resolver. If not installed, you can install it via pip:
  ```bash
  pip install uv
  ```

## Setup Instructions

1.  **Clone the Repository (Optional)**
    If you're setting this up from a Git repository:
    ```bash
    git clone git@github.com:tankwin08/mcp_rag_ollama.git
    cd mcp_rag_ollama
    ```
    If you're working in an existing local directory, you can skip this step.

2.  **Initialize Project with `uv` (if not already done)**
    If this is a new project directory and you haven't initialized `uv` yet:
    ```bash
    uv init
    ```
    This will create a `pyproject.toml` file if one doesn't exist.

    in this repo, we already have a `pyproject.toml` file, so we can skip this step.

    
3.  **Create and Activate Virtual Environment**
    ```bash
    uv venv
    ```
    Activate the environment (for macOS/Linux):
    ```bash
    source .venv/bin/activate
    ```
    For Windows (PowerShell):
    ```powershell
    .venv\Scripts\Activate.ps1
    ```

4.  **Install Dependencies**

    Because I already shared the toml file, we just need to sync using below command which will sync the `pyproject.toml` file with the current environment.
    
    If using `pyproject.toml`:
    ```bash
    uv sync
    ```
    If you have a `requirements.txt` file:
    ```bash
    uv pip install -r requirements.txt
    ```
    Common dependencies for such a project might include:
    ```bash
    uv add langchain langchain-community langchain-ollama mcp-server-framework tavily-python faiss-cpu python-dotenv beautifulsoup4
    ```
    *(Adjust the `uv add ...` command above based on your actual project dependencies. `mcp-server-framework` is a placeholder for the actual MCP package name if it's different.)*

5.  **Set Up Ollama Models**
    Pull the necessary models for Ollama. You'll typically need an embedding model and a chat/generation model.
    ```bash
    ollama pull nomic-embed-text
    ollama pull deepseek-r1 # Or mistral, or any other model you plan to use
    ```
    Ensure Ollama is running in the background.

6.  **Environment Variables**
    Create a `.env` file in the root of your project directory to store API keys or other configurations. For example, if you're using Tavily for search:
    ```plaintext:.env
    TAVILY_API_KEY="your_tavily_api_key_here"
    # Add other environment variables if needed
    # e.g., OPENAI_API_KEY if you were using OpenAI models
    ```

## Running the Application

Describe how to run your main application script. This might be an agent script or a server.

**Example for an agent script (e.g., `agent.py`):**

```bash
python agent.py
```

**Example for a server script (e.g., `server.py` using FastMCP):**
The `FastMCP` server usually starts automatically when the script is run.
```bash
python server.py
```
You would then interact with it via its defined tools/endpoints, possibly through another client or UI.

## Usage

Provide examples of how to interact with your RAG system.
- If it's a command-line agent, show example queries.
- If it's an MCP server, explain how to call its tools (e.g., using `mcp_client` or HTTP requests if it exposes an API).

**Example Query for Agent:**
```
"What are the latest advancements in AI according to recent web searches?"
```

## Project Structure (Optional)

Briefly describe the key files and their roles:
- `agent.py`: Main script for running the RAG agent (if applicable).
- `server.py`: Main script for running the MCP server (if applicable).
- `search.py`: Module for handling web search functionalities (e.g., using Tavily).
- `rag.py`: Module for RAG logic, including vector store creation and querying.
- `.env`: Stores environment variables (API keys, etc.).
- `pyproject.toml`: Project metadata and dependencies for `uv`.
- `README.md`: This file.

## Deactivating the Environment
When you're done working on the project:
```bash
deactivate
```



