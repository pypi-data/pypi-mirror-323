---

# Abstract APIs

The `abstract_apis` module is designed to facilitate HTTP requests in Python applications, particularly those that require handling JSON data, dealing with custom API endpoints, and parsing complex nested JSON responses. The module simplifies request handling by abstracting away common tasks such as header management, URL construction, and response parsing.

## Features

- **Header Management**: Automatically prepares headers suitable for JSON requests.
- **URL Construction**: Helps in constructing URLs by cleanly appending endpoints to base URLs.
- **Nested JSON Parsing**: Capable of parsing deeply nested JSON responses automatically to facilitate easy data extraction.
- **Flexible Response Handling**: Offers functions to handle both raw and parsed JSON responses based on user preference.
- **Error Handling**: Provides robust error reporting to aid in troubleshooting issues during HTTP requests.

## Installation

This module is not yet available on PyPI. To install, you can clone the repository and install it manually:

```bash
git clone https://github.com/AbstractEndeavors/abstract_apis.git
cd abstract_apis
python setup.py install
```

## Usage

### Making a GET Request

```python
from abstract_apis import getGetRequest

url = 'https://api.example.com'
endpoint = 'data'
params = {'key': 'value'}
response = getGetRequest(url, data=params, endpoint=endpoint)
print(response)
```

### Making a POST Request

```python
from abstract_apis import getPostRequest

url = 'https://api.example.com'
endpoint = 'submit'
data = {'key': 'value'}
response = getPostRequest(url, data=data, endpoint=endpoint)
print(response)
```

### Handling Nested JSON

The module automatically parses nested JSON responses if enabled:

```python
response = getGetRequest(url, data=params, endpoint=endpoint, load_nested_json=True)
print(response)
```

## Dependencies

- Python 3.6 or higher
- `requests` library

Make sure you have the `requests` library installed:

```bash
pip install requests
```

## Contributions

Contributions are welcome. Please fork the repository, make your changes, and submit a pull request on GitHub.

## Contact

For any questions or to discuss potential partnerships, please email [partners@abstractendeavors.com](mailto:partners@abstractendeavors.com).

## Contributions

Contributions are welcome! Please fork the [repository on GitHub](https://github.com/AbstractEndeavors/abstract_apis) and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

---

