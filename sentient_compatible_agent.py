import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import json
from typing import Dict, Any

load_dotenv()

class SearchAgent:
    def __init__(self):
        self.name = "SearchAgent"
    
    async def process_query(self, query_data: Dict[str, Any]) -> str:
        """Process search query in Sentient Framework format"""
        try:
            # Extract the prompt from the query object
            prompt = query_data.get("prompt", "")
            if not prompt:
                return "No prompt provided in query"
            
            # Perform search
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                return "Tavily API key not found"
            
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_api_key,
                    "query": prompt,
                    "search_depth": "basic"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                if results.get('results'):
                    return f"Search results for '{prompt}': {results['results'][0]['content']}"
                else:
                    return f"No results found for '{prompt}'"
            else:
                return f"Search failed: {response.text}"
                
        except Exception as e:
            return f"Error processing query: {str(e)}"

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

agent = SearchAgent()

@app.post("/assist")
async def assist_endpoint(request: dict):
    """
    Sentient Framework compatible endpoint
    Expects: {"query": {"prompt": "your search query"}}
    """
    try:
        # Extract query object from request
        query_obj = request.get("query", {})
        
        if not query_obj:
            return {"error": "Query object is required"}
        
        result = await agent.process_query(query_obj)
        return {"response": result}
        
    except Exception as e:
        return {"error": f"Failed to process request: {str(e)}"}

@app.post("/search")
async def search_endpoint(request: dict):
    """Simple search endpoint"""
    query = request.get("query", "")
    if not query:
        return {"error": "Query parameter is required"}
    
    result = await agent.process_query({"prompt": query})
    return {"response": result}

@app.get("/")
async def root():
    return {"message": "Sentient Framework Compatible Search Agent", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting Sentient Framework Compatible Search Agent")
    print("Endpoint: POST http://localhost:8000/assist")
    print("Expected format: {'query': {'prompt': 'your search query'}}")
    print("Simple format: POST http://localhost:8000/search with {'query': 'your search query'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)