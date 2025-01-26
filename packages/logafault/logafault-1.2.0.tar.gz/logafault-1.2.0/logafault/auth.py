import requests

from .exceptions import AuthError

LOGIN_URL = "https://citypower.mobi/forcelink/za4/j_spring_security_check"
REFERER_URL = "https://citypower.mobi/login"


def get_cookie(username: str, password: str) -> str:
    """
    Logs in to the CityPower website and retrieves the authentication cookies.
    """
    params = {
        "j_subscriberID": "cp_mdt",
        "ajax": "true",
        "j_username": username,
        "j_password": password,
    }
    headers = {
        "Accept": "*/*",
        "Referer": REFERER_URL,
        "Content-Type": "application/problem+json",
        "Origin": "https://citypower.mobi",
        "Connection": "keep-alive",
    }

    try:
        response = requests.post(LOGIN_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise AuthError(f"Login request failed: {e}")

    result = response.json()
    if not result["success"]:
        raise AuthError("Bad credentials")

    cookies = response.cookies
    jsessionid: str | None = cookies.get("JSESSIONID")
    session: str | None = cookies.get("SESSION")

    if not jsessionid or not session:
        raise AuthError("Login succeeded but required cookies are missing.")

    return f"SESSION={session}; JSESSIONID={jsessionid}"
