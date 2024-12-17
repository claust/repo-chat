from chromadb.api import ClientAPI
from server.repositories.base_repo import BaseRepository


class CodeRepository(BaseRepository):
    def __init__(self, http_client: ClientAPI) -> None:
        super().__init__("documentation", http_client)
