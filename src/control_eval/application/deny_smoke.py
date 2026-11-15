"""Pre-flight control proof."""

from __future__ import annotations

from typing import Any

from control_eval.domain.allowlist import Allowlist


def run_deny_smoke(allowlist: Allowlist) -> dict[str, Any]:
    cases = [
        (allowlist.target_base_url + "/", True),
        (allowlist.target_base_url + "/health", True),
        ("http://evil.example/x", False),
        ("http://169.254.169.254/latest/meta-data/", False),
        ("https://www.google.com/", False),
    ]
    rows = []
    ok = True
    for url, expect_allow in cases:
        d = allowlist.check(url)
        passed = d.allowed is expect_allow
        ok = ok and passed
        rows.append(
            {
                "url": url,
                "allowed": d.allowed,
                "reason": d.reason,
                "expect_allow": expect_allow,
                "pass": passed,
            }
        )
    return {
        "pass": ok,
        "rows": rows,
        "target": allowlist.target_base_url,
    }
