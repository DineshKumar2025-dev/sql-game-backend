from app.main import app
import os

def _database_url() -> str:
    return os.environ["POSTGRES_URL"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)