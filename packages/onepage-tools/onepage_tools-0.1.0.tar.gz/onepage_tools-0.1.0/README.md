## Usage

**Importing the Library**

You can import the library’s public API to interact with the tools.

```bash
from onepage_tools import PublicAPI

# Create an instance of the public API class
api = PublicAPI()

# Validate a token
token = "your_api_token_here"
result = api.validate_token(token)
print(result)

# Search for a person or company
search_result = api.search(token, "company or person query")
print(search_result)
```

**Running Tests**

To run tests, ensure you have pytest installed and use the following command:
```bash
pytest
```

**Compiling with Cython **
The internal logic of this library has been compiled using Cython to improve security and performance. To recompile or build the package, run:
```bash
python setup.py build_ext --inplace
```