"""HTTP port — adapters implement allowlist-gated requests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class HttpResponse:
    status_code: int
    url: str
    body: str
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)


class HttpPort(Protocol):
    def get(self, url_or_path: str) -> HttpResponse | str: ...

    def post_json(
        self, url_or_path: str, payload: dict[str, Any] | None = None
    ) -> HttpResponse | str: ...

    def upload_file(
        self, url_or_path: str, filename: str, content: bytes, field_name: str = "file"
    ) -> HttpResponse | str: ...

    def cookie_names(self) -> list[str]: ...
