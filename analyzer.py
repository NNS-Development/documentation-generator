import os
import zlib
import base64
import getpass
import binascii
from parser import Parser, REVREP

# API imports
from google import genai
from google.genai import types

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
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key is None:
        print("No API key found in environment.")
        print("Input your Google Gemini API key. (It will not be displayed)")
        api_key = getpass.getpass("> ")
    else:
        print("Using API key from environment.")
        
    return api_key


def generate(prompt: str) -> str:
    """
    Generate documentation using Google's Gemini API.
    """
    print("Setting up Gemini API...")
    api_key = get_api_key()
    
    # Initialize client and model
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    tools = [
        types.Tool(code_execution=types.ToolCodeExecution),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        top_p=0.5,
        max_output_tokens=8192,
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT),
        ],
    )

    print("Generating documentation using Gemini's API...")
    response_chunks = []

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (not chunk.candidates or 
            not chunk.candidates[0].content or 
            not chunk.candidates[0].content.parts):
            continue
            
        if chunk.candidates[0].content.parts[0].text:
            response_chunks.append(chunk.candidates[0].content.parts[0].text)
    
    response_str = "".join(response_chunks)

    # Calculate token usage
    print("Calculating token usage...")
    prompt_content = [
        types.Content(
            role="user", 
            parts=[types.Part.from_text(text=prompt)]
        )
    ]
    prompt_tokens = client.models.count_tokens(
        model=model, 
        contents=prompt_content
    ).total_tokens

    response_content = [
        types.Content(
            role="model", 
            parts=[types.Part.from_text(text=response_str)]
        )
    ]
    response_tokens = client.models.count_tokens(
        model=model, 
        contents=response_content
    ).total_tokens

    tokenusage = [
        "\nToken Usage:\n",
        f"Prompt tokens:               {prompt_tokens}\n",
        f"Response tokens:             {response_tokens}\n",
        f"Total tokens:                {prompt_tokens + response_tokens}\n"
    ]

    tokenusagestr = "".join(tokenusage)

    print(tokenusagestr)
    
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
        file.writelines(documentation)

    # Display token usage and completion message
    print("Documentation generated and saved to documentation.md")