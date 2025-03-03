import os
import zlib
import base64
import getpass
import binascii
from parser import Parser, REVREP

# API imports
import openai
import tiktoken

"""
Analyzer module for the documentation generator.

uses gemini's api to generate documentation
"""

_revrep_items = [f"'{k}': '{v}'" for k, v in REVREP.items()]
_revrep_dict = "{" + ", ".join(_revrep_items) + "}"

SYSTEM_PROMPT = f"""You are an expert Python documentation writer with deep knowledge of decoding, code analysis, and AST interpretation.
You will be provided with a string of encoded text. You are to follow the steps below strictly. 

Step 1: Decode the encoded text
When you receive the encoded text, use the snippet below to decode it. Do NOT generate documentation for this:
```
import base64, zlib, ast
def unrep(s):
    i = {_revrep_dict}
    for l, x in i.items():
        s = s.replace(l, x)
    return s
def decompress(c):
    return ast.unparse(ast.parse(u(zlib.decompress(base64.b64decode(c)).decode('utf-8'))))
```
After running `decompress` on the encoded text, the returned value will be a python AST. 
Proceed on to the next step. 

Step 2: Analyze the AST
- Using the AST from step 1, analyze and understand how the code works by inspecting its structure.
- Identify functions, classes, methods, key algorithms, and dependencies.
- Verify correctness and highlight any unusual patterns.

Step 3: Generate comprehensive documentation in markdown. 
Use your analysis of the code to create a well-structured documentation using the following format:

1. Project Overview
- Purpose and functionality of the code
- High-level architecture/design patterns used
- Key features

2. Technical Documentation
Classes:
For each class:
- Name and inheritance
- Purpose and responsibilities
- Attributes and types
- Method descriptions with:
* Parameters and types
* Return values
* Side effects
* Usage examples

Functions
For each function:
- Signature
- Purpose
- Parameters and types
- Return values and types
- Examples with expected outputs
- Exceptions raised (if any)

3. Dependencies
- External packages with versions
- System requirements

4. Implementation Details
- Key algorithms explained
- Important design decisions
- Performance considerations
- Threading/async behavior (if any)

5. Usage Guide
- Installation instructions
- Configuration requirements
- Code examples for common use cases
- Best practices

6. Notes and Warnings
- Known limitations
- Common pitfalls
- Security considerations (if applicable)

Additional Guidelines:
- Format the documentation in clean, well-structured Markdown.
- Use ```python for code examples.
- Infer and document any implicit behaviors or patterns.
- If certain aspects cannot be determined from the AST alone, clearly note this in the documentation.

Focus only on generating documentation in well-formatted markdown and avoid assumptions about the AST structure beyond what is explicitly provided.
"""


def decompress_ast(compressed: str) -> str:
    try:
        decoded = base64.b64decode(compressed)
        decompressed = zlib.decompress(decoded)
        return Parser.unreplacek(decompressed.decode('utf-8'))
    except (binascii.Error, zlib.error) as e:
        raise ValueError(f"Decompression failed: {e}")


def get_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if api_key is None:
        print("No API key found in environment.")
        print("Input your OpenAI API key. (It will not be displayed)")
        api_key = getpass.getpass("> ")
    else:
        print("Using API key from environment.")
        
    return api_key



def generate(prompt: str) -> str:
    """
    Generate documentation using OpenAI's ChatGPT API.
    """
    print("Setting up OpenAI API...")
    api_key = get_api_key()
    client = openai.OpenAI(api_key=api_key)
    model = "gpt-4"
    encoding = tiktoken.encoding_for_model(model)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    print("Generating documentation using ChatGPT's API...")
    response_str = ""

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            top_p=0.5,
            max_tokens=8192,
            stream=True,
        )

        # Stream the response content as per the documentation example
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            response_str += content

    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {e}")

    print("Calculating token usage...")
    prompt_tokens = sum(len(encoding.encode(msg["content"])) for msg in messages)
    response_tokens = len(encoding.encode(response_str))

    token_usage = [
        "\nToken Usage:\n",
        f"Prompt tokens:               {prompt_tokens}\n",
        f"Response tokens:             {response_tokens}\n",
        f"Total tokens:                {prompt_tokens + response_tokens}\n"
    ]
    print("".join(token_usage))
    
    return response_str

def analyze(compressed_ast: str) -> str:
    """
    Analyze and generate documentation.
    """
    if len(compressed_ast) > 80: 
        preview = compressed_ast[:77] + "..."
    else:
        preview = compressed_ast
        
    print(f"Compressed code: {preview}\n")
    
    # Generate documentation from the compressed AST
    print("Analyzing code structure and generating documentation...")
    documentation = generate(compressed_ast)

    return documentation


if __name__ == "__main__":
    # Parse and compress this file
    print("Parsing and compressing analyzer.py...")
    p = Parser("analyzer.py")
    compressed_ast, profiler = p.parse()
    
    # Generate documentation
    documentation = analyze(compressed_ast)

    # Save output to file
    print("Saving documentation to file...")
    with open("documentation.md", "w", encoding="utf-8") as file:
        file.write(documentation)

    print("Documentation generated and saved to documentation.md")