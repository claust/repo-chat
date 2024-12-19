from typing import List
from chromadb import HttpClient, Metadata, QueryResult, Where
from chromadb.api import ClientAPI
from chromadb.api.types import ID, Document, OneOrMany


class BaseRepository():
    def __init__(self, collection_name: str, http_client: ClientAPI | None) -> None:
        if http_client is None:
            http_client = HttpClient(host="localhost", port=8000)
        self._chroma_client = http_client
        self._collection = self._chroma_client.get_or_create_collection(
            collection_name)

    def name(self) -> str:
        return self._collection.name

    def count(self) -> int:
        return self._collection.count()

    def upsert(self, ids: OneOrMany[ID], docs: OneOrMany[Document], metadatas: OneOrMany[Metadata] | None = None) -> None:
        self._collection.upsert(ids, documents=docs, metadatas=metadatas)

    def remove_docs(self, ids: list) -> None:
        self._collection.delete(ids=ids)

    def get_by_id(self, id: OneOrMany[ID]) -> List[Document] | None:
        return self._collection.get(id, include=["documents"])["documents"]

    def get_all_ids(self) -> List[str]:
        return self._collection.peek(limit=100000)['ids']

    def query_all_ids(self, where: Where | None) -> List[str]:
        result: QueryResult = self._collection.query(
            # Empty query to get all documents. Does this actually work?
            query_texts=[""],
            where=where, n_results=100000)
        return result["ids"][0]

    def search(self, query: str, metadata: Metadata | None = None) -> List[str] | None:
        result: List[str] = self._collection.query(
            query_texts=[query], n_results=5, where=metadata)
        return result["documents"][0]
