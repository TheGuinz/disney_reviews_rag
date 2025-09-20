# Stampli Disneyland Review Q&A
This project is a FastAPI application that acts as a Q&A service for Disneyland reviews, powered by a local Large Language Model. It features robust performance monitoring to track API traffic and LLM latency.

## Features
Query Endpoint: A /query endpoint that accepts user questions and returns a generated answer from the LLM.

- Local LLM Integration: The application is configured to use a local Ollama model (llama3.1:8b) for all Q&A logic, eliminating the need for external API calls to services like OpenAI.

- Asynchronous Operations: The application uses asyncio to handle blocking operations like the LLM invocation in a separate thread, ensuring the API remains responsive and non-blocking.

## Performance Monitoring:

- Request Counter: A database-backed counter tracks the total number of requests to the API.

- LLM Latency: Dedicated logging within the /query endpoint captures the specific time taken for the LLM's response, allowing for granular performance analysis of the most critical component.

## Installation & Setup

1. Clone the repository:
2. `git clone <your_repo_url>`
3. `cd <your_project_directory>`
4. Install Ollama: Download and install Ollama from the official website. This will set up the local server needed to run the LLM.
5. Pull the LLM and Embedding Models:
The application uses a separate model for generating text embeddings, which are numerical representations of the text. These embeddings are crucial for the Retrieval-Augmented Generation (RAG) process, allowing the system to quickly find the most relevant document chunks from the Disneyland reviews.
6. Pull the specific models used in this project from the terminal:
  <br> 6.1 `ollama pull llama3.1:8b`
  <br> 6.2 `ollama pull nomic-embed-text:latest` (The nomic-embed-text model is a powerful, open-source embedding model that is specifically trained to create high-quality vector embeddings. It's a key component for the FAISS vector store used in the RAG pipeline.)
7. Install Python dependencies: `pip install -r requirements.txt`. 
8. Run the application: Start the server using Uvicorn. `python run.py` (The application will be running at `http://127.0.0.1:8000`)

## Usage
To interact with the API, send a POST request to the /query endpoint with a JSON body containing your question.

- Query Request
  - Request:<br>
    `curl -X 'POST' \
      'http://localhost:8000/query' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "query": "Is spring a good time to visit Disneyland?"
    }'`
  - Response:<br>
    `{"answer":"Based on the reviews, it seems that two reviewers (Review_ID: 594712008 and Review_ID: 670570869) mentioned that March is a good time to visit Disneyland because of the good weather. Another reviewer (Review_ID: 660034324) also mentioned that March was a good time for them.\n\nHowever, one reviewer (Review_ID: 594712008) specifically mentioned that April or May are too hot and not recommended.\n\nSince spring in Hong Kong typically falls in March to May, it can be inferred that visiting Disneyland during this period might be a good idea due to the pleasant weather."}`

- Reset Requests Counter:
  `curl http://127.0.0.1:8000/reset_counter`
  
## Project Structure
- `main.py`: The core FastAPI application, including the main API endpoints and middleware.
- `db_utils.p`y: Contains utility functions for interacting with the SQLite database to manage the request counter.
- `services.py`: Handles the setup of the Retrieval-Augmented Generation (RAG) chain, including loading data, chunking documents, and initializing the Ollama LLM and embeddings.
- `requirements.txt`: Lists all the necessary Python packages for the project.