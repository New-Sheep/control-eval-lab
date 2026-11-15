"""URL allowlist — single source of truth for egress control (DRY)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse


BLOCKED_SCHEMES = frozenset({"file", "php", "gopher", "data", "jar", "ftp", "javascript"})
LINK_LOCAL_PREFIXES = ("169.254.", "metadata")


@dataclass(frozen=True, slots=True)
class AllowlistDecision:
    allowed: bool
    reason: str
    normalized_url: str | None = None


class Allowlist:
    """
    Only the configured target host:port may be contacted.
    Metadata / link-local / exotic schemes are always denied.
    """

    def __init__(self, target_base_url: str) -> None:
        base = (target_base_url or "").strip().rstrip("/")
        if not base:
            raise ValueError("target_base_url must be non-empty")
        if "://" not in base:
            base = f"http://{base}"
        parsed = urlparse(base)
        host = (parsed.hostname or "").lower()
        if not host:
            raise ValueError(f"invalid target_base_url: {target_base_url!r}")
        scheme = (parsed.scheme or "http").lower()
        port = parsed.port or (443 if scheme == "https" else 80)
        self._base = base
        self._scheme = scheme
        self._host = host
        self._port = port

    @property
    def target_base_url(self) -> str:
        return self._base

    def resolve(self, url_or_path: str) -> str:
        raw = (url_or_path or "").strip()
        if not raw:
            return self._base + "/"
        if "://" not in raw:
            return urljoin(self._base + "/", raw.lstrip("/"))
        return raw

    def check(self, url_or_path: str) -> AllowlistDecision:
        full = self.resolve(url_or_path)
        parsed = urlparse(full)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        port = parsed.port or (443 if scheme == "https" else 80)

        if scheme in BLOCKED_SCHEMES or scheme not in ("http", "https"):
            return AllowlistDecision(False, f"blocked_scheme:{scheme}", None)
        if not host:
            return AllowlistDecision(False, "missing_host", None)
        if host == "metadata.google.internal" or any(
            host.startswith(p) for p in LINK_LOCAL_PREFIXES
        ):
            return AllowlistDecision(False, "blocked_metadata_or_link_local", None)
        if host in ("169.254.169.254", "metadata"):
            return AllowlistDecision(False, "blocked_metadata_or_link_local", None)
        if host != self._host or port != self._port or scheme != self._scheme:
            return AllowlistDecision(False, f"host_not_allowlisted:{host}", None)
        return AllowlistDecision(True, "allow", full)
