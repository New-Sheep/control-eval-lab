"""Playwright BrowserPort — optional; falls back with clear errors if missing."""

from __future__ import annotations

import concurrent.futures
import time
from typing import Any, Callable
from urllib.parse import urlparse

from control_eval.domain.allowlist import Allowlist
from control_eval.ports.corpus import CorpusPort


class PlaywrightBrowser:
    def __init__(
        self,
        allowlist: Allowlist,
        *,
        corpus: CorpusPort | None = None,
        guest_cookie_header: str = "",
    ) -> None:
        self._allowlist = allowlist
        self._corpus = corpus
        self._guest_cookie = guest_cookie_header
        self._pw: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None
        self._network: list[dict[str, Any]] = []
        self._exec = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="pw"
        )

    def _run(self, fn: Callable[[], Any], timeout: float = 90.0) -> Any:
        return self._exec.submit(fn).result(timeout=timeout)

    def _cookie_domain(self) -> str:
        return urlparse(self._allowlist.target_base_url).hostname or "127.0.0.1"

    def _seed(self, context: Any) -> list[str]:
        names: list[str] = []
        for part in (self._guest_cookie or "").split(";"):
            part = part.strip()
            if "=" not in part:
                continue
            n, v = part.split("=", 1)
            n, v = n.strip(), v.strip()
            if not n:
                continue
            context.add_cookies(
                [
                    {
                        "name": n,
                        "value": v,
                        "domain": self._cookie_domain(),
                        "path": "/",
                    }
                ]
            )
            names.append(n)
        return names

    def open(self) -> dict[str, Any]:
        def _do() -> dict[str, Any]:
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                return {
                    "ok": False,
                    "error": "playwright_not_installed — pip install 'control-eval-lab[browser]'",
                }
            if self._page is not None:
                return {"ok": True, "already_open": True, "url": self._page.url}
            self._network = []
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=True)
            self._context = self._browser.new_context(
                user_agent="ControlEvalLab/0.1",
                viewport={"width": 1280, "height": 900},
            )
            seeded = self._seed(self._context)
            self._page = self._context.new_page()

            def _on_resp(response: Any) -> None:
                try:
                    url = response.url
                    d = self._allowlist.check(url)
                    if not d.allowed:
                        return
                    req = response.request
                    if req.resource_type not in ("xhr", "fetch", "document"):
                        return
                    body = ""
                    try:
                        body = (response.text() or "")[:300]
                    except Exception:  # noqa: BLE001
                        pass
                    self._network.append(
                        {
                            "method": req.method,
                            "url": url,
                            "status": response.status,
                            "body_preview": body,
                            "ts": time.time(),
                        }
                    )
                    if len(self._network) > 80:
                        del self._network[:40]
                except Exception:  # noqa: BLE001
                    pass

            self._page.on("response", _on_resp)
            return {
                "ok": True,
                "seeded_cookies": seeded,
                "target": self._allowlist.target_base_url,
            }

        return self._run(_do)

    def close(self) -> dict[str, Any]:
        def _do() -> dict[str, Any]:
            try:
                if self._context:
                    self._context.close()
                if self._browser:
                    self._browser.close()
                if self._pw:
                    self._pw.stop()
            except Exception:  # noqa: BLE001
                pass
            self._pw = self._browser = self._context = self._page = None
            self._network = []
            return {"ok": True, "closed": True}

        return self._run(_do)

    def goto(self, url_or_path: str) -> dict[str, Any] | str:
        d = self._allowlist.check(url_or_path)
        if not d.allowed:
            return f"BLOCKED:{d.reason} url={self._allowlist.resolve(url_or_path)}"

        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            resp = self._page.goto(
                d.normalized_url, wait_until="domcontentloaded", timeout=45_000
            )
            return {
                "ok": True,
                "url": self._page.url,
                "status": resp.status if resp else None,
                "title": self._page.title(),
            }

        return self._run(_do, timeout=60.0)

    def snapshot(self) -> dict[str, Any] | str:
        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            controls: list[dict[str, str]] = []
            for role in ("button", "link", "textbox"):
                try:
                    for loc in self._page.get_by_role(role).all()[:20]:
                        name = (
                            loc.get_attribute("aria-label") or loc.inner_text() or ""
                        )[:80].strip()
                        controls.append({"role": role, "name": name})
                except Exception:  # noqa: BLE001
                    continue
            for loc in self._page.locator('input[type="file"]').all()[:5]:
                controls.append(
                    {
                        "role": "file",
                        "name": loc.get_attribute("name") or "file",
                        "selector": 'input[type="file"]',
                    }
                )
            body = ""
            try:
                body = (self._page.locator("body").inner_text(timeout=5_000) or "")[
                    :3000
                ]
            except Exception:  # noqa: BLE001
                pass
            return {
                "url": self._page.url,
                "title": self._page.title(),
                "controls": controls[:50],
                "body_text_preview": body,
            }

        return self._run(_do)

    def click(
        self, *, role: str = "", name: str = "", selector: str = ""
    ) -> dict[str, Any] | str:
        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            if selector.strip():
                self._page.locator(selector).first.click(timeout=15_000)
                how = f"selector={selector}"
            elif role.strip() and name.strip():
                self._page.get_by_role(role, name=name, exact=False).first.click(
                    timeout=15_000
                )
                how = f"role={role} name={name}"
            elif name.strip():
                self._page.get_by_text(name, exact=False).first.click(timeout=15_000)
                how = f"text={name}"
            else:
                return "ERROR:need_role_name_or_selector"
            self._page.wait_for_timeout(300)
            return {"ok": True, "clicked": how, "url": self._page.url}

        return self._run(_do)

    def fill(
        self,
        value: str,
        *,
        role: str = "textbox",
        name: str = "",
        selector: str = "",
    ) -> dict[str, Any] | str:
        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            if selector.strip():
                self._page.locator(selector).first.fill(value, timeout=15_000)
                how = f"selector={selector}"
            elif name.strip():
                self._page.get_by_role(role or "textbox", name=name, exact=False).first.fill(
                    value, timeout=15_000
                )
                how = f"role={role} name={name}"
            else:
                return "ERROR:need_name_or_selector"
            return {"ok": True, "filled": how}

        return self._run(_do)

    def upload(
        self, corpus_name: str, *, selector: str = 'input[type="file"]'
    ) -> dict[str, Any] | str:
        if self._corpus is None:
            return "ERROR:corpus_unavailable"
        path = self._corpus.resolve(corpus_name)
        if not path:
            return f"ERROR:corpus_not_allowlisted:{corpus_name}"

        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            self._page.locator(selector).first.set_input_files(str(path), timeout=20_000)
            self._page.wait_for_timeout(300)
            return {
                "ok": True,
                "corpus_name": corpus_name,
                "bytes": path.stat().st_size,
                "url": self._page.url,
            }

        return self._run(_do)

    def network(self, limit: int = 20) -> dict[str, Any] | str:
        def _do() -> dict[str, Any] | str:
            if self._page is None:
                return "ERROR:browser_not_open"
            n = max(1, min(int(limit or 20), 40))
            return {"url": self._page.url, "events": self._network[-n:], "count": n}

        return self._run(_do)
