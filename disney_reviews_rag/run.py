import os
import logging
import uvicorn
from dotenv import load_dotenv


load_dotenv()
PORT = int(os.environ.get("PORT", 8000))  # Default to port 8000
HOST = os.environ.get("HOST", "0.0.0.0")  # Default to '0.0.0.0'

# prevent macOS runtime crashes
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# set logging level
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logging.getLogger("faiss.loader").setLevel(logging.WARNING)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)