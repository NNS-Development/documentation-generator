import warnings
import os
from parser import Parser
import analyzer

# Suppress GRPC warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def stripartifacts(docs: str) -> str:
    project_overview_index = docs.find("# Project Overview")

    if project_overview_index != -1:
        docs = docs[project_overview_index:]

    docs = docs[:-3] if docs.endswith('```') else docs

    return docs

def main() -> None:
    """
    Main entry point
    """
    # Welcome message
    print("Documentation generator")
    # Parse the analyzer.py file and get its compressed AST
    parser = Parser("analyzer.py")
    compressed_ast, profiler = parser.parse()
    # Analyze the compressed AST and generate documentation
    documentation, tokenusage = analyzer.analyze(compressed_ast)

    print("Removing artifacts...")
    documentation = stripartifacts(documentation)
    print("Writing to file...")
    # Save the generated documentation to a file
    with open("documentation.md", "w", encoding="utf-8") as file:
        file.writelines(documentation)
    print()
    print("Done!")
    # Print token usage statistics
    print(tokenusage)
    print("Documentation generated and saved to documentation.md")


if __name__ == "__main__":
    main()