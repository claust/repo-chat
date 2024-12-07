from typing import List
import chromadb


class CodeRepository():
    def __init__(self, host='localhost', port=8000, collection_name='repo-chat'):
        self._chroma_client = chromadb.HttpClient(host=host, port=port)
        self._collection = self._chroma_client.get_or_create_collection(
            collection_name)

    def name(self) -> str:
        return self._collection.name

    def collection(self) -> chromadb.Collection:
        return self._collection

    def count(self) -> int:
        return self._collection.count()

    def upsert(self, ids, docs) -> None:
        self._collection.upsert(ids, documents=docs)

    def remove_docs(self, ids: list) -> None:
        self._collection.delete(ids=ids)

    def get_all_ids(self) -> List[str]:
        return self._collection.peek(limit=1000)['ids']
