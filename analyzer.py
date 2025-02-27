import os
import zlib
import base64
import getpass
import binascii
import warnings
from parser import Parser
from google import genai
from google.genai import types
from typing import List, Tuple
from parser import REVREP
# Suppress GRPC warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

revrep_items = [f"'{k}': '{v}'" for k, v in REVREP.items()]
revrep_dict = "{" + ", ".join(revrep_items) + "}"

SYSTEM_PROMPT=f"""You are an expert Python documentation writer with deep knowledge of decoding, code analysis, and AST interpretation.
You will be provided with a string of encoded text. You are to follow the steps below strictly. 

Step 1: Decode the encoded text
When you receive the encoded text, use the snipped below to decode it. Do NOT generate documentation for this. :
```
import base64, zlib, ast
def unrep(s):
    i = {revrep_dict}
    for l, x in i.items():
        s = s.replace(l, x)
    return s
def decompress(c):
    return ast.unparse(ast.parse(unrep(zlib.decompress(base64.b64decode(c)).decode('utf-8'))))
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

def generate(prompt: str) -> Tuple[str, str]:
    print("Searching for your API key...")
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if API_KEY is None:
        print("No API key found.")
        print("Input your Google Gemini API key. (It will not be displayed)")
        API_KEY = getpass.getpass("> ")
    else:
        print("Using API key in environment.")

    print("Initializing model...")

    client = genai.Client(
        api_key=API_KEY,
    )

    model = "gemini-2.0-flash"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=prompt
                ),
            ],
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
            types.Part.from_text(
                text=SYSTEM_PROMPT
            ),
        ],
    )

    print("Generating documentation using Gemini's API...")

    response = []

    for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].text:
            response.append(chunk.candidates[0].content.parts[0].text)
    
    response_str = "".join(response)

    print("Counting tokens...")

    # For prompt tokens
    prompt_content = [types.Content(
        role="user", 
        parts=[
            types.Part.from_text(prompt)
            ]
    )]
    prompt_tokens = client.models.count_tokens(model=model, contents=prompt_content).total_tokens

    # For response tokens
    response_content = [types.Content(
        role="model", parts=[
            types.Part.from_text(response_str)
        ]
    )]
    response_tokens = client.models.count_tokens(model=model, contents=response_content).total_tokens

    tokenusage: List[str] = []
    tokenusage.append("\nToken Usage:\n")
    tokenusage.append(f"Prompt tokens:               {prompt_tokens}\n")
    tokenusage.append(f"Response tokens:             {response_tokens}\n")
    tokenusage.append(f"Total tokens:                {prompt_tokens + response_tokens}\n")
    tokenusage_str = "".join(tokenusage)

    return response_str, tokenusage_str

def analyze(compressed_ast: str) -> Tuple[str, str]:
    '''entry point'''
    # Generate documentation
    print(f"Compressed code: {compressed_ast}")
    print("Analyzing code...")
    documentation, tokenusage = generate(compressed_ast)
    
    return documentation, f"{tokenusage}\n\nDocumentation generated and saved to documentation.md"

if __name__ == "__main__":
    p = Parser("analyzer.py")
    compressed_ast, profiler = p.parse()
    documentation, tokenusage = analyze(compressed_ast)

    with open("documentation.md", "w") as file:
        file.writelines(documentation)

    print(tokenusage)