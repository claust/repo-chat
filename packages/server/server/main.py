from fastapi import FastAPI

from server.indexer import indexer

# To run server in dev mode:
# fastapi dev server/main.py --port 8080

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Repo Chat server is running"}


@app.get('/indexer')
def index_repo() -> dict[str, str]:
    result: str = indexer()
    return {"message": "Indexer", "result": result}
