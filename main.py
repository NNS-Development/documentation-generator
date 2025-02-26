from parser import Parser
from analyzer import analyze as analyze_main
import sys

"""
main.py

Main script that coordinates between parser.py and analyzer.py to:
1. Parse a Python file into an AST
2. Compress the AST
3. Generate documentation using Gemini API
"""

def main_dep() -> None:
    # gits filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter Python file to parse (or press Enter for 'test.py'): ").strip() or "test.py"

    try:
        # Initialize parser
        print(f"\nInitializing parser for {filename}...")
        parser = Parser(filename)

        # Parse and compress the file
        print("Parsing and compressing file...")
        compressed_ast = parser.parse()
        print(compressed_ast)
        # Generate documentation
        print("\nGenerating documentation using Gemini API...")
        analyze_main(compressed_ast)

        print("\nProcess completed successfully!")
        print("You can find the generated documentation in 'documentation.md'")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def helpusage() -> str:
    return""

def main() -> None:
    '''main loop'''
    # get filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter path to python file (Enter for test.py): ").strip() or "test.py"
    
    if filename in {"-h", "--help"}:
        print("TODO: print help")

if __name__ == "__main__":
    main()