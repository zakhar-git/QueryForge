from queryforge.detection import detect_candidates, validate_value


def test_detection():
    assert "email" in detect_candidates("analyst@example.com")
    assert "ip" in detect_candidates("8.8.8.8")
    assert "domain" in detect_candidates("example.com")
    assert "hash" in detect_candidates("a" * 64)
    assert "crypto_address" in detect_candidates("0x0000000000000000000000000000000000000000")
    assert "github_repo" in detect_candidates("octocat/Hello-World")


def test_validation():
    assert validate_value("email", "analyst@example.com")
    assert not validate_value("email", "invalid")
    assert validate_value("ip", "2001:4860:4860::8888")
    assert validate_value("domain", "example.com")
