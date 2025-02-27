# Project Overview

This project provides a tool for automatically generating documentation for Python code using Google's Gemini API. It takes compressed Python AST code as input, decompresses it, and then uses the Gemini API to generate comprehensive documentation in Markdown format.

- **Purpose and Functionality:** The primary goal is to automate the documentation process for Python projects by leveraging the capabilities of large language models.
- **High-level Architecture:** The code consists of several functions that handle different stages of the documentation generation process: decompressing the AST, interacting with the Gemini API, and formatting the output. It uses the `parser` module for AST manipulation and `google.genai` for interacting with the Gemini API.
- **Key Features:**
    - Decompresses compressed Python AST code.
    - Interacts with Google's Gemini API to generate documentation.
    - Formats the generated documentation in Markdown.
    - Provides token usage statistics.

# Technical Documentation

## Classes

There are no classes defined in this code.

## Functions

### `decompress_ast(compressed: str) -> str`

- **Purpose:** Decompresses a base64 and zlib compressed string representing a Python AST and returns the unparsed Python code.
- **Parameters:**
    - `compressed` (str): The compressed string.
- **Return Value:**
    - `str`: The decompressed Python code.
- **Exceptions Raised:**
    - `ValueError`: If decompression fails due to `binascii.Error` or `zlib.error`.
- **Example:**
```python
compressed_code = "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"
decompressed_code = decompress_ast(compressed_code)
print(decompressed_code)
```

### `get_api_key() -> str`

- **Purpose:** Retrieves the Google Gemini API key from the environment variables or prompts the user to enter it.
- **Parameters:**
    - None
- **Return Value:**
    - `str`: The API key.
- **Side Effects:**
    - Prints messages to the console.
    - May prompt the user for input.
- **Example:**
```python
api_key = get_api_key()
print(f"API Key: {api_key}") # The actual key will not be printed, but a message will be shown.
```

### `generate(prompt: str) -> Tuple[str, str]`

- **Purpose:** Generates documentation using Google's Gemini API based on the provided prompt.
- **Parameters:**
    - `prompt` (str): The prompt to send to the Gemini API.
- **Return Value:**
    - `Tuple[str, str]`: A tuple containing the generated documentation and token usage statistics.
- **Side Effects:**
    - Prints messages to the console.
    - Interacts with the Google Gemini API.
- **Example:**
```python
prompt = "Write documentation for a function that adds two numbers."
documentation, token_usage = generate(prompt)
print(documentation)
print(token_usage)
```

### `analyze(compressed_ast: str) -> Tuple[str, str]`

- **Purpose:** Analyzes a compressed AST and generates documentation.
- **Parameters:**
    - `compressed_ast` (str): The compressed AST code.
- **Return Value:**
    - `Tuple[str, str]`: A tuple containing the generated documentation and token usage statistics.
- **Side Effects:**
    - Prints messages to the console.
    - Calls the `generate` function.
- **Example:**
```python
compressed_ast = "some_compressed_ast_code"
documentation, token_usage = analyze(compressed_ast)
print(documentation)
print(token_usage)
```

# Dependencies

- os
- zlib
- base64
- getpass
- binascii
- warnings
- typing
- parser
- google
- google.genai

# Implementation Details

- **Key Algorithms:**
    - The code uses zlib and base64 for compression and decompression of the AST.
    - It uses Google's Gemini API for generating documentation from the decompressed AST.
- **Important Design Decisions:**
    - The code uses a system prompt to guide the Gemini API in generating documentation.
    - It uses streaming to handle large responses from the Gemini API.
- **Performance Considerations:**
    - The code uses token counting to track the usage of the Gemini API.

# Usage Guide

1.  **Installation Instructions:**
    - Install the required packages: `pip install google-generativeai`
2.  **Configuration Requirements:**
    - Set the `GEMINI_API_KEY` environment variable with your Google Gemini API key.
3.  **Code Examples:**
    ```python
    import os
    import zlib
    import base64
    import getpass
    import binascii
    import warnings
    from typing import Tuple
    from parser import Parser, REVREP
    import google.genai as genai
    from google.genai import types

    # (Define the functions decompress_ast, get_api_key, generate, and analyze as in the decompressed code)

    if __name__ == '__main__':
        # Create a dummy Parser object and compressed AST for demonstration
        class DummyParser:
            def parse(self):
                return "compressed_ast_code", "profiler_data"
        p = DummyParser()
        compressed_ast = "compressed_ast_code" # Replace with actual compressed AST
        documentation, tokenusage = analyze(compressed_ast)
        print(documentation)
        print(tokenusage)
    ```
4.  **Best Practices:**
    - Ensure that the `GEMINI_API_KEY` environment variable is set before running the code.
    - Use a descriptive prompt to guide the Gemini API in generating documentation.

# Notes and Warnings

- **Known Limitations:**
    - The quality of the generated documentation depends on the quality of the prompt and the capabilities of the Gemini API.
- **Common Pitfalls:**
    - Ensure that the compressed AST code is valid.
    - Handle API rate limits and errors gracefully.
- **Security Considerations:**
    - Store the Gemini API key securely and avoid exposing it in the code.
