from pathlib import Path
from typing import IO, Any, Literal

from _typeshed import Incomplete

from .endpoints import Endpoints as Endpoints
from .endpoints import RequestMethod as RequestMethod
from .exceptions import APIKeyMissingError as APIKeyMissingError
from .releases import AllReleases as AllReleases
from .settings import VerboseLevel as VerboseLevel
from .settings import logger as logger

COSMOS_PLATFORM_BACKEND_URL: str

class CosmosClient:
    apikey: Incomplete
    server_url: Incomplete
    verbose: Incomplete
    session: Incomplete

    def __init__(
        self,
        apikey: str | None = None,
        server_url: str | None = ...,
        verbose: VerboseLevel = ...,
    ) -> None: ...
    def status_health_request(self) -> dict[str, Any] | None: ...
    def translate_text_request(
        self,
        text: str,
        output_language: str,
        input_language: str | None = None,
    ) -> dict[str, Any] | None: ...
    def translate_file_request(
        self,
        filepath: Path | str,
        output_language: str,
        input_language: str | None = None,
        return_type: Literal["raw_text", "url", "file"] = "raw_text",
    ) -> dict[str, Any] | None: ...
    def web_search_request(
        self,
        text: str,
        output_language: str | None = None,
        desired_urls: list[str] | str | None = None,
    ) -> dict[str, Any] | None: ...
    def llm_chat_request(self, text: str, model: str | None = None) -> dict[str, Any] | None: ...
    def llm_embed_request(self, text: str) -> dict[str, Any] | None: ...
    def files_parse_request(
        self,
        filepath: Path,
        extract_type: Literal["subchunks", "chunks", "pages", "file"] = "subchunks",
        k_min: int | None = None,
        k_max: int | None = None,
        overlap: int | None = None,
        filter_pages: str | None = None,
    ) -> dict[str, Any] | None: ...
    def files_index_create_request(
        self,
        name: str,
        filepaths: list[Path] | list[str] | None = None,
        filesobjects: list[tuple[str, tuple[str, IO[bytes]]]] | None = None,
    ) -> dict[str, Any] | None: ...
    def files_index_add_files_request(
        self,
        index_uuid: str,
        filepaths: list[Path] | list[str] | None = None,
        filesobjects: list[tuple[str, tuple[str, IO[bytes]]]] | None = None,
    ) -> dict[str, Any] | None: ...
    def files_index_delete_files_request(self, index_uuid: str, files_hashes: list[str]) -> dict[str, Any] | None: ...
    def files_index_delete_request(self, index_uuid: str) -> dict[str, Any] | None: ...
    def files_index_restore_request(self, index_uuid: str) -> dict[str, Any] | None: ...
    def files_index_rename_request(self, index_uuid: str, name: str) -> dict[str, Any] | None: ...
    def files_index_ask_request(
        self,
        index_uuid: str,
        question: str,
        output_language: str | None = None,
        active_files_hashes: list[str] | None = None,
    ) -> dict[str, Any] | None: ...
    def files_index_embed_request(self, index_uuid: str) -> dict[str, Any] | None: ...
    def files_index_details_request(self, index_uuid: str) -> dict[str, Any] | None: ...
    def files_index_list_request(self) -> dict[str, Any] | None: ...
