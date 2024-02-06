import uvicorn
from dotenv import load_dotenv
from app.api import api

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)