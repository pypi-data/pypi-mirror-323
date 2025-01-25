# pynebis

Pynebis is a Python client for interacting with Nebis, an in-memory database with disk persistence, designed to be ultra-fast, scalable, and easy to use.

## Features

- Secure data storage.
- Local and server synchronization.
- Full CRUD operations (Create, Read, Update, Delete).
- In-memory data handling with configurable TTL (Time-to-Live).

## Installation

Install the package using pip:

```bash
pip install nebis
```

## Usage

### Basic Example:

```python
from nebis_sdk import NebisSDK

n = NebisSDK("nebis://user:pass@host/db", m='method')
n.c({"key": "1", "value": {"name": "John"}})
print(n.r())
```

### Detailed Usage:

```python
from nebis_sdk import NebisSDK

try:
    # Connect to the database
    n = NebisSDK("nebis://user:pass@nebisdb.pythonanywhere.com/db", m='both')

    # Create (Save) data
    s = {
        "key": "1",
        "value": {
            "name": "John",
            "lastname": "Smith",
        }
    }
    n.c(s)

    # Read data
    l = n.r()
    print(l)

    # Update data
    u = {
        "key": "1",
        "value": {
            "name": "Luke",
            "lastname": "Smith",
            "age": 25
        }
    }
    n.u(u)

    # Delete data
    k = {"key": "1"}
    n.d(k)

except Exception as e:
    print(str(e))
```

## Available Methods

- `c(data)`: Stores data in memory, locally, and on the server based on the configuration.
- `r()`: Retrieves stored data.
- `u(data)`: Updates existing data.
- `d(data)`: Deletes data from storage.

## Configuration Parameters

- `m`: Storage mode (`local`, `server`, `both`).
- `ttl`: Time-to-live for in-memory data (default: 300 seconds).

## License

This project is licensed under the [LICENSE](LICENSE).

## Contributing

Feel free to submit issues or pull requests to improve Pynebis. Contributions are welcome!

