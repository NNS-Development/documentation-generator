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
    SYSTEM_PROMPT = """You are a technical documentation expert. Analyze the provided Python AST and generate detailed documentation in markdown format. Include:

1. Overview of the code's purpose
2. Detailed function/class documentation
3. Usage examples where appropriate
4. Any important implementation details
5. Dependencies and requirements

Please format the output in clean, readable markdown."""

    # Start chat and send decompressed AST
    chat = model.start_chat(history=[])
    decompressed = decompress_ast(compressed_ast)
    
    response = chat.send_message(f"{SYSTEM_PROMPT}\n\nCode AST:\n{decompressed}")
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