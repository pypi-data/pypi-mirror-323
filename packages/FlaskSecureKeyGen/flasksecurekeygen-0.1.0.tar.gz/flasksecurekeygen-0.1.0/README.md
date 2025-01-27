# FlaskSecureKeyGen

FlaskSecureKeyGen is a Python library designed to generate secure, random secret keys for Flask applications. It ensures that your Flask app's secret keys are cryptographically strong and suitable for production use.

## Installation

You can install FlaskSecureKeyGen using pip:

```bash
pip install FlaskSecureKeyGen
```

## Usage

### 1. Generating a Secret Key

The main functionality of this library is to generate secure secret keys. You can use the `generate_secret_key` function from the `keygen` module.

```python
from flask_secure_keygen import generate_secret_key

# Generate a 64-character secret key
secret_key = generate_secret_key(64)
print(secret_key)
```

**Parameters:**
- `length`: The length of the secret key (default is 64). Must be at least 32 characters for security.

**Example Output:**
```plaintext
3a1f8e4d7c9b2a5f6e8c9d0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
```

### 2. Using Utility Functions

The library also provides utility functions in the `utils` module to help validate key lengths.

```python
from flask_secure_keygen.utils import validate_key_length

# Check if a key length is valid
is_valid = validate_key_length(40)
print(is_valid)  # Output: True
```

**Parameters:**
- `length`: The desired key length to validate.

**Returns:**
- `True` if the length is valid (i.e., 32 or more characters).
- `False` otherwise.

### 3. Integrating with Flask

You can use the generated secret key directly in your Flask application.

```python
from flask import Flask
from flask_secure_keygen import generate_secret_key

app = Flask(__name__)

# Generate and set a secure secret key for the Flask app
app.secret_key = generate_secret_key(64)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run(debug=True)
```

## Why Use FlaskSecureKeyGen?

- **Secure**: Uses Python's `secrets` module to generate cryptographically strong random keys.
- **Simple**: Just one function to generate keys of any length (minimum 32 characters).
- **Customizable**: You can specify the length of the key as per your requirements.
- **Utility Functions**: Additional utility functions to validate key lengths.

## Modules Overview

### 1. `keygen` Module
This module contains the main functionality for generating secret keys.

- `generate_secret_key(length=64):`
  Generates a secure random secret key of the specified length.

### 2. `utils` Module
This module provides utility functions for additional functionality.

- `validate_key_length(length):`
  Validates if the provided key length is secure (at least 32 characters).

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue on the GitHub repository.

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Made with Love by Ch. Abdul Wahab
