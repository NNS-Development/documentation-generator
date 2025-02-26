import warnings
import base64
import os
from google import genai
from google.genai import types
# Suppress GRPC warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



def generate(inputstr: str) -> str:
  client = genai.Client(
        api_key=input("API Key"),
  )

  model = "gemini-2.0-flash"
  contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=inputstr
                ),
            ],
        ),
    ]
  tools = [
      types.Tool(code_execution=types.ToolCodeExecution),
  ]
  generate_content_config = types.GenerateContentConfig(
      temperature=0,
      top_p=0.95,
      top_k=40,
      max_output_tokens=8192,
      tools=tools,
      response_mime_type="text/plain",
      system_instruction=[
          types.Part.from_text(
              text="""You are an expert Python documentation writer with deep knowledge of decoding and decrypting, code analysis, and AST interpretation.
        You will be provided with a string of encoded text. Follow these steps:
        
        Step 1: Decode the Input String
        Use the following Python snippet to decode the string:
        ```python
        import base64, zlib, ast
        
        def unrep(s):
            i = {
                'FV': 'FormattedValue', 'FD': 'FunctionDef', 'EX': 'ExceptHandler', 'IF': 'ImportFrom', 'AA': 'AnnAssign',
                'ATT': 'Attribute', 'ARG': 'arguments', 'SS': 'Subscript', 'CO': 'Constant', 'CD': 'ClassDef', 'UO': 'UnaryOp',
                'K': 'keyword', 'ST': 'Starred', 'R': 'Return', 'AS': 'Assign', 'I': 'Import', 'M': 'Module', 'AL': 'alias',
                'S': 'Store', 'val': 'value', 'C': 'Call', 'E': 'Expr', 'N': 'Name', 'L': 'Load'
            }
            for l, x in i.items():
                s = s.replace(l, x)
            return s
        
        def decompress(c):
            return ast.unparse(ast.parse(unrep(zlib.decompress(base64.b64decode(c)).decode('utf-8'))))
        ```
        You must decode and analyze the AST but do **not** output the decoded content directly.
        
        Step 2: Analyze the AST
        - Understand how the code works by inspecting its structure.
        - Identify functions, classes, methods, key algorithms, and dependencies.
        - Verify correctness and highlight any unusual patterns.
        
        Step 3: Generate Comprehensive Documentation
        Create well-structured documentation using the following format:
        
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
        
        Focus only on generating documentation and avoid assumptions about the AST structure beyond what is explicitly provided.
        """
          ),
      ],
  )

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

    prompt_tokens = client.models.count_tokens(
        model=model,
        contents=prompt,
    ).total_tokens

    response_tokens = client.models.count_tokens(
        model=model,
        contents=inputstr
    ).total_tokens

    print("\nToken Usage:")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
    print(f"Total tokens: {prompt_tokens + response_tokens}")
    return response

def analyze_code(compressed_ast: str) -> str:
    '''analyzes code using gemini api'''
    prompt = SYSTEM_PROMPT
    response = generate(prompt, compressed_ast)

    response_str = "".join(response)

    return response_str

def _analyze_code(compressed_ast: str) -> str:
    """
    ! DEPRECATED !
    Analyze code using Gemini API and generate documentation
    """
    
    # Configure API
    API_KEY = os.getenv("GEMINI_API_KEY")
    if API_KEY is None:
        API_KEY = input("Input your Gemini API key: ")
    else:
        print("using api key in environment.")
    genai.configure(api_key=API_KEY)
    print("Generating documentation...")
    # Configure generation parameters
    generation_config = {
        "temperature": 0,
        "top_p": 0.55,
        "max_output_tokens": 16384,
        "tools": ""
    }

    # Initialize model
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config # type: ignore
    )

    # Start chat and send decompressed AST
    chat = model.start_chat()
    
    prompt = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=compressed_ast
                ),
            ],
        ),
    ]

    # Count tokens in the prompt
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

def analyze(compressed_ast):
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
    analyze(compressed_ast)