"""Browser port — Playwright (or stub) behind this interface."""

from __future__ import annotations

from typing import Any, Protocol


class BrowserPort(Protocol):
    def open(self) -> dict[str, Any]: ...

    def close(self) -> dict[str, Any]: ...

    def goto(self, url_or_path: str) -> dict[str, Any] | str: ...

    def snapshot(self) -> dict[str, Any] | str: ...

    def click(
        self, *, role: str = "", name: str = "", selector: str = ""
    ) -> dict[str, Any] | str: ...

    def fill(
        self,
        value: str,
        *,
        role: str = "textbox",
        name: str = "",
        selector: str = "",
    ) -> dict[str, Any] | str: ...

    def upload(
        self, corpus_name: str, *, selector: str = 'input[type="file"]'
    ) -> dict[str, Any] | str: ...

    def network(self, limit: int = 20) -> dict[str, Any] | str: ...
