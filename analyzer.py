import warnings
import os, sys
import base64
import zlib
from dotenv import load_dotenv
import google.generativeai as genai
from parser import Parser
# Suppress GRPC warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

"""
analyzer.py

Gets the encoded string from parser.py using Parser.zlibcomp()
Analyzes the decompressed code using Gemini API
Generates documentation
"""

SYSTEM_PROMPT = """You are an expert Python documentation writer with deep knowledge of code analysis and AST interpretation. 
You will be provided with a string of encrypted text, and you are to decrypt it with this:
```
import base64, zlib, ast
def u(s):
    i={'FV':'FormattedValue','FD':'FunctionDef','EX':'ExceptHandler','IF':'ImportFrom','AA':'AnnAssign','ATT':'Attribute','ARG':'arguments','SS':'Subscript','CO':'Constant','CD':'ClassDef','UO':'UnaryOp','K':'keyword','ST':'Starred','R':'Return','AS':'Assign','I':'Import','M':'Module','AL':'alias','S':'Store','val':'value','C':'Call','E':'Expr','N':'Name','L':'Load'}
    for l,x in i.items():s=s.replace(l,x)
    return s
def decompress(c):
    return ast.unparse(ast.parse(u(zlib.decompress(base64.b64decode(c)).decode('utf-8'))))
```
Your task is to analyze the decrypted text, which will be a AST and generate comprehensive documentation.
Structure your documentation with these specifications:
1. Project Overview
- Main purpose and functionality of the code
- High-level architecture/design patterns used
- Key features
2. Technical Documentation
For each class:
- Class name and inheritance
- Purpose and responsibilities 
- Class attributes and their types
- Method descriptions with:
* Parameters and their types
* Return values
* Side effects
* Usage examples
For each function:
- Function signature
- Purpose
- Parameters and their types
- Return value and type
- Examples with expected outputs
- Any exceptions raised
3. Dependencies
- Required external packages and their versions
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
Format the documentation in clean, well-structured markdown with appropriate headers, code blocks, and lists. Use ```python for code examples.
Based on the AST structure, infer and document any implicit behaviors or patterns. If certain aspects cannot be determined from the AST alone, note this in the documentation.
Try to keep code snippets short. 
Only output the documentation and nothing else."""

load_dotenv()

def decompress_ast(compressed: str) -> str:
    """Decompress a base64+zlib compressed AST string"""
    decoded = base64.b64decode(compressed)
    decompressed = zlib.decompress(decoded)
    return Parser.unreplacek(decompressed.decode('utf-8'))

def analyze_code(compressed_ast: str) -> str:
    """Analyze code using Gemini API and generate documentation"""
    
    # Configure API
    API_KEY = os.getenv("GEMINI_API_KEY")
    if API_KEY is None:
        API_KEY = input("Input your Gemini API key: ")
    else:
        print("using api key from environment.")
    genai.configure(api_key=API_KEY)
    print("Generating documentation...")

    # Configure generation parameters
    generation_config = {
        "temperature": 0,
        "top_p": 0.5,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05",
        generation_config=generation_config, # type: ignore
        system_instruction=SYSTEM_PROMPT,
        tools='code_execution',
    )

    # Start chat and send decompressed AST
    chat = model.start_chat()
    
    # Count tokens in the prompt
    prompt_tokens = model.count_tokens(compressed_ast).total_tokens
    
    # Send message and get response
    response = chat.send_message(compressed_ast)
    
    # Count tokens in the response
    response_tokens = model.count_tokens(response.text).total_tokens
    
    # Print token usage
    print("\nToken Usage:")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
    print(f"Total tokens: {prompt_tokens + response_tokens}")
    
    return "\n  ".join(response.text.splitlines()[1:-1])

def main(compressed_ast):
    '''entry point'''
    # Generate documentation
    documentation = analyze_code(compressed_ast)
    
    # Save to file
    with open("documentation.md", "w") as f:
        f.write(documentation)
    
    print("Documentation generated and saved to documentation.md")

if __name__ == "__main__":
    p = Parser("main.py")
    compressed_ast = p.parse()
    main(compressed_ast)