from typing import List
from chromadb import Collection, HttpClient, QueryResult


class CodeRepository():
    def __init__(self, host='localhost', port=8000) -> None:

        self._chroma_client = HttpClient(host=host, port=port)
        self._collection_code = self._chroma_client.get_or_create_collection(
            'repo-chat')

    def name(self) -> str:
        return self._collection_code.name

    def collection(self) -> Collection:
        return self._collection_code

    def count(self) -> int:
        return self._collection_code.count()

    def upsert(self, ids, docs) -> None:
        self._collection_code.upsert(ids, documents=docs)

    def remove_docs(self, ids: list) -> None:
        self._collection_code.delete(ids=ids)

    def get_all_ids(self) -> List[str]:
        return self._collection_code.peek(limit=100000)['ids']

    def search(self, query: str) -> List[List[str]] | None:
        result: QueryResult = self._collection_code.query(
            query_texts=[query], n_results=5)
        return result["documents"]
