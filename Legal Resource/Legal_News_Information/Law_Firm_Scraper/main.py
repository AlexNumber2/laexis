from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
from scraper import scrape_all_firms

# CRITICAL FIX for Windows: This must be executed before uvicorn starts the server
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Laexis Law Firm Scraper API")

# Allow the frontend Legal_Resources.html to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
async def search_law_firms(q: str):
    """
    Receives the keyword 'q' from the HTML frontend, sweeps the targeted
    law firm sites for data, and returns a JSON list.
    """
    try:
        print(f"Starting search across law firms for keyword: {q}")
        
        # Call the scraper function which handles running Playwright operations
        all_results = await scrape_all_firms(q)
        
        print(f"Search complete. Found {len(all_results)} results total.")
        return {"status": "success", "data": all_results}
        
    except Exception as e:
        print(f"Error during search execution: {e}")
        return {"status": "error", "message": str(e), "data": []}

# Command to run this server has changed. Do NOT use `uvicorn main:app` directly.
# Run replacing with: python main.py
if __name__ == "__main__":
    import uvicorn
    # By running uvicorn programmatically, our WindowsProactorEventLoopPolicy setting takes effect.
    print("Starting Uvicorn Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
