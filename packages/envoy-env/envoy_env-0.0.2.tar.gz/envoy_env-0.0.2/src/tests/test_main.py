from envoy.__main__ import _is_env, _get_differences


def test_is_env_valid():
    """Test that _is_env works with some valid inputs"""
    assert _is_env("TEST_1=testing")
    assert _is_env("TEST_2=")
    assert _is_env("ENV=")


def test_is_env_ignore_comments():
    """Test that _is_env ignores comments containing env vars"""
    assert not _is_env("# TEST_1=testing")
    assert not _is_env("#TEST_2=")
    assert not _is_env("# # # ENV=")


def test_invalid_lines():
    """Test that _is_env ignores some invalid lines"""
    assert not _is_env("TEST_1")
    assert not _is_env("")
    assert not _is_env(" ")


def test_get_differences_valid():
    """Test that get_differences works for valid cases"""
    differences = _get_differences(
        "tests/assets/001_env_valid.env", "tests/assets/001.env.example")

    assert differences == []


def test_get_differences_missing():
    """Test that get_differences works for missing cases"""
    differences = _get_differences(
        "tests/assets/001_missing_test_2.env", "tests/assets/001.env.example")

    assert differences == ["TEST_2"]

    differences = _get_differences(
        "tests/assets/001_missing_test_1.env", "tests/assets/001.env.example")

    assert differences == ["TEST_1"]
