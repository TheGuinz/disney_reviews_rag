import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from .services import setup_qa_chain
from .db_utils import init_db, get_counter, increment_counter, reset_counter
import logging


logger = logging.getLogger("\t  " + __name__.strip())

app = FastAPI(
    title="Stampli Disneyland Review Q&A",
    description="Stampli ML Engineer Home assignment",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

class ResetResponse(BaseModel):
    message: str
    
@app.on_event("startup")
async def startup_event():
    """
    Initialize the database when the app starts.
    """

    global qa_chain
    
    qa_chain = setup_qa_chain()
    if qa_chain is None:
        return HTTPException(status_code=500, content={"detail": "Failed to initialize the Q&A chain. Check your data file path and dependencies."})
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Disneyland Review QA API. Use the /docs endpoint to see the available endpoints."}

@app.get("/reset_counter", response_model=ResetResponse)
async def handle_reset():
    """
    Endpoint to reset the current value of the query counter.
    """
    await asyncio.to_thread(reset_counter)
    return {"message": "Counter has been reset to zero."}

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Handles a query request by processing it and logging the counter,
    and then invokes the LLM chain.
    """

    global qa_chain

    try:   
        # invoke on seperate thread to avoid blocking
        await asyncio.to_thread(lambda: increment_counter())
        # same
        counter_value = await asyncio.to_thread(lambda: get_counter())
        start_invoke_time = time.time()
        # same
        result = await asyncio.to_thread(qa_chain.invoke, {"query": request.query})
        end_invoke_time = time.time()
        invoke_latency = end_invoke_time - start_invoke_time

        logger.info(f"Request Counter: {counter_value} | LLM Invoke Latency: {invoke_latency:.4f}s")

        return QueryResponse(answer=result["result"])
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        return HTTPException(status_code=500, content={"detail": str(e)})