"""Allowlist-gated httpx client (HttpPort)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from control_eval.domain.allowlist import Allowlist
from control_eval.domain.findings import FindingStore
from control_eval.domain.policy import ToolBudget
from control_eval.ports.http import HttpResponse


class HttpxClient:
    def __init__(
        self,
        allowlist: Allowlist,
        *,
        findings: FindingStore | None = None,
        budget: ToolBudget | None = None,
        timeout: float = 20.0,
    ) -> None:
        self._allowlist = allowlist
        self._findings = findings or FindingStore()
        self._budget = budget or ToolBudget()
        self._jar = httpx.Cookies()
        self._timeout = timeout
        host = urlparse(allowlist.target_base_url).hostname or "127.0.0.1"
        self._cookie_domain = host

    def cookie_names(self) -> list[str]:
        try:
            return sorted({c.name for c in self._jar.jar})  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            return []

    def seed_cookie_header(self, header: str) -> None:
        for part in (header or "").split(";"):
            part = part.strip()
            if "=" not in part:
                continue
            name, value = part.split("=", 1)
            name, value = name.strip(), value.strip()
            if name:
                self._jar.set(name, value, domain=self._cookie_domain, path="/")

    def _gate(self, url_or_path: str) -> tuple[str | None, str]:
        d = self._allowlist.check(url_or_path)
        if not d.allowed:
            self._findings.log(
                "allowlist_deny",
                detail={"url": url_or_path, "reason": d.reason},
                severity="high",
                tool="gate",
            )
            return None, f"BLOCKED:{d.reason} url={self._allowlist.resolve(url_or_path)}"
        return d.normalized_url, "ok"

    def _ingest_cookies(self, resp: httpx.Response) -> None:
        items = (
            resp.headers.multi_items()
            if hasattr(resp.headers, "multi_items")
            else list(resp.headers.items())
        )
        for k, v in items:
            if k.lower() != "set-cookie":
                continue
            first = (v or "").split(";", 1)[0]
            if "=" not in first:
                continue
            name, value = first.split("=", 1)
            name, value = name.strip(), value.strip()
            if name:
                try:
                    self._jar.set(name, value, domain=self._cookie_domain, path="/")
                except Exception:  # noqa: BLE001
                    pass

    def _pack(self, resp: httpx.Response, *, max_body: int = 24_000) -> HttpResponse:
        self._ingest_cookies(resp)
        return HttpResponse(
            status_code=resp.status_code,
            url=str(resp.url),
            body=(resp.text or "")[:max_body],
            headers={k: v for k, v in list(resp.headers.items())[:40]},
            cookies={n: self._jar.get(n) or "" for n in self.cookie_names()},
        )

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self._timeout,
            follow_redirects=True,
            cookies=self._jar,
            headers={
                "User-Agent": "ControlEvalLab/0.1",
                "Accept": "application/json,text/html,*/*",
            },
        )

    def get(self, url_or_path: str) -> HttpResponse | str:
        err = self._budget.bump()
        if err:
            return err
        allowed, msg = self._gate(url_or_path)
        if not allowed:
            return msg
        try:
            with self._client() as c:
                resp = c.get(allowed)
            self._findings.log(
                "tool",
                tool="http_get",
                detail={"url": allowed, "status": resp.status_code},
            )
            return self._pack(resp)
        except Exception as e:  # noqa: BLE001
            return f"ERROR:{type(e).__name__}:{e}"

    def post_json(
        self, url_or_path: str, payload: dict[str, Any] | None = None
    ) -> HttpResponse | str:
        err = self._budget.bump()
        if err:
            return err
        allowed, msg = self._gate(url_or_path)
        if not allowed:
            return msg
        try:
            with self._client() as c:
                resp = c.post(allowed, json=payload or {})
            self._findings.log(
                "tool",
                tool="http_post_json",
                detail={"url": allowed, "status": resp.status_code},
            )
            return self._pack(resp)
        except Exception as e:  # noqa: BLE001
            return f"ERROR:{type(e).__name__}:{e}"

    def upload_file(
        self,
        url_or_path: str,
        filename: str,
        content: bytes,
        field_name: str = "file",
    ) -> HttpResponse | str:
        err = self._budget.bump()
        if err:
            return err
        allowed, msg = self._gate(url_or_path)
        if not allowed:
            return msg
        try:
            with self._client() as c:
                resp = c.post(
                    allowed,
                    files={field_name: (filename, content)},
                )
            self._findings.log(
                "tool",
                tool="upload_file",
                severity="medium",
                detail={
                    "url": allowed,
                    "status": resp.status_code,
                    "filename": filename,
                },
            )
            return self._pack(resp)
        except Exception as e:  # noqa: BLE001
            return f"ERROR:{type(e).__name__}:{e}"
