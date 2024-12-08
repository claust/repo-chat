from typing import List
from chromadb import Collection, HttpClient, QueryResult
from chromadb.api import ClientAPI


class BaseRepository():
    def __init__(self, collection: str, http_client: ClientAPI = HttpClient(host="localhost", port=8000)) -> None:
        self._chroma_client = http_client
        self._collection = self._chroma_client.get_or_create_collection(
            collection)

    def name(self) -> str:
        return self._collection.name

    def collection(self) -> Collection:
        return self._collection

    def count(self) -> int:
        return self._collection.count()

    def upsert(self, ids, docs) -> None:
        self._collection.upsert(ids, documents=docs)

    def remove_docs(self, ids: list) -> None:
        self._collection.delete(ids=ids)

    def get_all_ids(self) -> List[str]:
        return self._collection.peek(limit=100000)['ids']

    def search(self, query: str) -> List[List[str]] | None:
        result: QueryResult = self._collection.query(
            query_texts=[query], n_results=5)
        return result["documents"]
