"""
analyzer.py

Gets the encoded string from parser.py using Parser.zlibcomp()
Analyzes the decompressed code using Gemini API
Generates documentation
"""
import warnings
import os
# Suppress GRPC warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import base64
import zlib
import google.generativeai as genai
from typing import Dict

def unreplacek(s: str) -> str:
    """Replace shortened tokens with their original keywords"""
    replacements: Dict[str, str] = {
        "FormattedValue": "FV", "FunctionDef": "FD", "ExceptHandler": "EX",
        "ImportFrom": "IF", "AnnAssign": "AA", "Attribute": "ATT", 
        "arguments": "ARG", "Subscript": "SS", "Constant": "CO",
        "ClassDef": "CD", "UnaryOp": "UO", "keyword": "K",
        "Starred": "ST", "Return": "R", "Assign": "AS",
        "Import": "I", "Module": "M", "alias": "AL",
        "Store": "S", "value": "val", "Call": "C",
        "Expr": "E", "Name": "N", "Load": "L"
    }
    
    revreplacements = {v: k for k, v in replacements.items()}
    for long, short in revreplacements.items():
        s = s.replace(long, short)
    return s

def decompress_ast(compressed: str) -> str:
    """Decompress a base64+zlib compressed AST string"""
    decoded = base64.b64decode(compressed)
    decompressed = zlib.decompress(decoded)
    return unreplacek(decompressed.decode('utf-8'))

def analyze_code(compressed_ast: str) -> str:
    """Analyze code using Gemini API and generate documentation"""
    
    # Configure API
    api_key = input("Input your Gemini API key: ")
    genai.configure(api_key=api_key)

    # Configure generation parameters
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

    # Initialize model
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config
    )


    # System prompt
    SYSTEM_PROMPT = """You are an expert Python documentation writer with deep knowledge of code analysis and AST interpretation. Your task is to analyze the provided Python Abstract Syntax Tree (AST) and generate comprehensive, professional documentation.
    
    Please structure your documentation following these specific sections:
    
    1. # Project Overview
       - Main purpose and functionality of the code
       - High-level architecture/design patterns used
       - Key features
    
    2. # Technical Documentation
       ## Classes
       For each class:
       - Class name and inheritance
       - Purpose and responsibilities 
       - Class attributes and their types
       - Method descriptions with:
         * Parameters and their types
         * Return values
         * Side effects
         * Usage examples
    
       ## Functions
       For each function:
       - Function signature
       - Purpose
       - Parameters and their types
       - Return value and type
       - Examples with expected outputs
       - Any exceptions raised
    
    3. # Dependencies
       - Required external packages
       - Version requirements
       - System requirements
    
    4. # Implementation Details
       - Key algorithms explained
       - Important design decisions
       - Performance considerations
       - Threading/async behavior (if any)
    
    5. # Usage Guide
       - Installation instructions
       - Configuration requirements
       - Code examples for common use cases
       - Best practices
    
    6. # Notes and Warnings
       - Known limitations
       - Common pitfalls
       - Security considerations (if applicable)
    
    Format the documentation in clean, well-structured markdown with appropriate headers, code blocks, and lists. Use ```python for code examples.
    
    Based on the AST structure, infer and document any implicit behaviors or patterns. If certain aspects cannot be determined from the AST alone, note this in the documentation.
    
    AST to analyze:
    """

    # Start chat and send decompressed AST
    chat = model.start_chat(history=[])
    decompressed = decompress_ast(compressed_ast)
    
    # Count tokens in the prompt
    prompt = f"{SYSTEM_PROMPT}\n\nCode AST:\n{decompressed}"
    prompt_tokens = model.count_tokens(prompt).total_tokens
    
    # Send message and get response
    response = chat.send_message(prompt)
    
    # Count tokens in the response
    response_tokens = model.count_tokens(response.text).total_tokens
    
    # Print token usage
    print("\nToken Usage:")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
    print(f"Total tokens: {prompt_tokens + response_tokens}")
    
    return response.text

def main(compressed_ast):

    
    # Generate documentation
    documentation = analyze_code(compressed_ast)
    
    # Save to file
    with open("documentation.md", "w") as f:
        f.write(documentation)
    
    print("Documentation generated and saved to documentation.md")

if __name__ == "__main__":
    main()