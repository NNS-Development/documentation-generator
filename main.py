"""
main.py

Main script that coordinates between parser.py and analyzer.py to:
1. Parse a Python file into an AST
2. Compress the AST
3. Generate documentation using Gemini API
"""

from parser import Parser
from analyzer import main as analyze_main
import sys

def main():
    # Get filename from command line args or prompt user
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
        parser.parsefile()
        compression_result = parser.zlibcomp()
        compressed_ast = compression_result[1]  # Get actual compressed string, not the length info

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

if __name__ == "__main__":
    main()