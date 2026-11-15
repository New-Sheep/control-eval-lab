from control_eval.domain.allowlist import Allowlist


def test_allows_target_health():
    al = Allowlist("http://127.0.0.1:8000")
    d = al.check("/health")
    assert d.allowed
    assert d.normalized_url == "http://127.0.0.1:8000/health"


def test_denies_evil():
    al = Allowlist("http://127.0.0.1:8000")
    d = al.check("http://evil.example/x")
    assert not d.allowed
    assert "host_not_allowlisted" in d.reason


def test_denies_metadata():
    al = Allowlist("http://127.0.0.1:8000")
    d = al.check("http://169.254.169.254/latest/meta-data/")
    assert not d.allowed
    assert "metadata" in d.reason


def test_denies_wrong_port():
    al = Allowlist("http://127.0.0.1:8000")
    d = al.check("http://127.0.0.1:9000/health")
    assert not d.allowed
