import pytest
from requests import HTTPError, RequestException

from logafault.auth import AuthError, get_cookie


@pytest.fixture
def mock_post(mocker):
    """Fixture to mock requests.post."""
    return mocker.patch("logafault.auth.requests.post")


def test_get_cookie_success(mock_post):
    # Mock response with cookies
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.cookies.get.side_effect = lambda name: {
        "JSESSIONID": "mock_jsessionid",
        "SESSION": "mock_session",
    }.get(name)

    cookie = get_cookie("valid_user", "valid_password")
    assert cookie == "SESSION=mock_session; JSESSIONID=mock_jsessionid"
    mock_post.assert_called_once()


def test_get_cookie_missing_cookies(mock_post):
    # Mock response without cookies
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.cookies.get.side_effect = lambda name: None

    with pytest.raises(AuthError, match="required cookies are missing"):
        get_cookie("valid_user", "valid_password")


def test_get_cookie_request_error(mock_post):
    # Simulate a request failure
    mock_post.side_effect = RequestException("Request failed")

    with pytest.raises(AuthError, match="Login request failed: Request failed"):
        get_cookie("valid_user", "valid_password")


def test_get_cookie_http_error(mock_post):
    # Mock response with HTTP error
    mock_response = mock_post.return_value
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError("HTTP 500 error")

    with pytest.raises(AuthError, match="Login request failed: HTTP 500 error"):
        get_cookie("valid_user", "valid_password")


def test_get_cookie_bad_credentials(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": False}

    with pytest.raises(AuthError, match="Bad credentials"):
        get_cookie("invalid_user", "invalid_password")
