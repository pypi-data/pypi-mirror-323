# `logafault` - SDK for Logging Faults with City Power

`logafault` is a Python SDK that allows users to programmatically log faults with City Power, provided they have a valid username and password. This package interacts with City Power's website and API to authenticate users, retrieve fault data, and log new faults.

## Installation

You can install `logafault` directly from PyPI:

```bash
pip install logafault
```

## Usage

### 1. Authenticate and Get Session Cookie

To interact with the City Power APIs, you first need to authenticate with your username and password to get a session cookie. This cookie is required for subsequent API requests.

```python
from logafault.auth import get_cookie, AuthError

# Replace with your City Power username and password
username = "your_username"
password = "your_password"

try:
    cookie = get_cookie(username, password)
    print("Successfully authenticated!")
except AuthError as e:
    print(f"Authentication failed: {e}")
```

### 2. Fetch All Logged Faults

Once authenticated, you can retrieve all logged faults associated with your account. The `get_all_faults` function fetches the list of faults.

```python
from logafault.faults import get_all_faults, FaultsAPIError

try:
    faults = get_all_faults(cookie)
    print("Logged faults:", faults)
except FaultsAPIError as e:
    print(f"Failed to fetch faults: {e}")
```

### 3. Log a New Fault

You can also log a new fault using the `log_fault` function. You will need to provide the necessary fault data in the form of a dictionary.

```python
from logafault.faults import log_fault, FaultsAPIError

# Sample fault data (replace with actual fault details)
fault_data = {
    "workType": "NS", # No Supply
    "childWorkType": "NSA", # No Supply (Area)
    "customLookupCode2": "Prepaid",
    "description": "My bat signal is off.",
    "custom2": "1234567890", # Meter Number
    "custom4": "", # Alternate Account Number
    "contactNumber": "0123456789",
    "contactName": "Bruce Wayne",
}

try:
    response = log_fault(cookie, fault_data)
    print("Fault logged successfully:", response)
except FaultsAPIError as e:
    print(f"Failed to log fault: {e}")
```

## Functions

### `get_cookie(username: str, password: str) -> str`
Logs in to the City Power website and retrieves the session cookies needed for authentication.

**Arguments:**
- `username` (str): The username for authentication.
- `password` (str): The password for authentication.

**Returns:**
- A string containing the session cookie for future requests.

**Raises:**
- `AuthError`: If login fails or required cookies are missing.

---

### `get_all_faults(cookie: str) -> list[dict]`
Fetches all logged faults from the City Power API.

**Arguments:**
- `cookie` (str): The session cookie to authenticate the request.

**Returns:**
- A list of dictionaries representing the logged faults.

**Raises:**
- `FaultsAPIError`: If the request fails or the response is invalid.

---

### `log_fault(cookie: str, fault_data: dict) -> dict`
Logs a new fault to the City Power API.

**Arguments:**
- `cookie` (str): The session cookie to authenticate the request.
- `fault_data` (dict): A dictionary containing fault details.

**Returns:**
- A dictionary with the API response containing the fault details.

**Raises:**
- `FaultsAPIError`: If the request fails or the response is invalid.

---

## Error Handling

### `AuthError`
This exception is raised if there is an issue with authentication, such as incorrect credentials or missing cookies.

### `FaultsAPIError`
This exception is raised if there is an issue with the faults API, including problems with fetching faults or logging a new fault.

---

## Development

If you want to contribute to the development of `logafault`, clone the repository and install the development dependencies:

```bash
git clone https://github.com/cliftondhanee/logafault.git
cd logafault
make setup-dev
```

### Running Tests

To run the unit tests:

```bash
make test
```

### Linting

We use `flake8` for linting. You can run it with:

```bash
make lint
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For more information, feel free to open an issue on GitHub or contact the author:

- **Author**: Clifton Dhanee
- **Email**: clifton.dhanee@yahoo.com

---
