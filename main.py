from parser import Parser
import analyzer

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
    print("Documentation generator")
    
    parser = Parser("analyzer.py")
    compressed_ast, profiler = parser.parse()
    
    documentation = analyzer.analyze(compressed_ast)

    print("Removing artifacts...")
    documentation = stripartifacts(documentation)
    
    print("Writing to file...")
    with open("documentation.md", "w", encoding="utf-8") as file:
        file.writelines(documentation)

    print("Documentation generated and saved to documentation.md")
    print("Done!")

if __name__ == "__main__":
    main()