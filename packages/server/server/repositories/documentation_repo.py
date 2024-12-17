from chromadb.api import ClientAPI
from server.repositories.base_repo import BaseRepository


class DocumentationRepository(BaseRepository):
    def __init__(self, http_client: ClientAPI | None = None) -> None:
        super().__init__("documentation", http_client)
