from abc import ABC, abstractmethod
from chromadb import Where
from chromadb.api import ClientAPI
from server.repositories.base_repo import BaseRepository


class DocumentationType(ABC):
    @abstractmethod
    def where(self) -> Where:
        pass


class SingleFileDocumentation(DocumentationType):
    def where(self) -> Where:
        return {"file_summary": True}


class FolderDocumentation(DocumentationType):
    def where(self) -> Where:
        return {"folder_summary": True}


class DocumentationRepository(BaseRepository):
    def __init__(self, http_client: ClientAPI | None = None) -> None:
        super().__init__("documentation", http_client)

    def query_all_ids_of_type(self, type: DocumentationType) -> list:
        return super().query_all_ids(where=type.where())
