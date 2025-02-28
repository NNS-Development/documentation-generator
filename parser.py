import re
import ast
import sys
import zlib
import base64
from typing import Optional, Tuple, Dict

"""
Parser module for the documentation generator.

parses and compresses python files
"""

# Mapping of AST node names to shorter versions for compression
REPLACEMENTS = {
    "FormattedValue": "~",
    "FunctionDef": "$",
    "ExceptHandler": "¢",
    "ImportFrom": "£",
    "AnnAssign": "¥",
    "Attribute": "§",
    "arguments": "©",
    "Subscript": "®",
    "Constant": "°",
    "ClassDef": "µ",
    "UnaryOp": "¶",
    "keyword": "†",
    "Starred": "‡",
    "Return": "Ω",
    "Assign": "√",
    "Import": "√",
    "Module": "∞",
    "alias": "≈",
    "Store": "≠",
    "value": "≤",
    "Call": "÷",
    "Expr": "‰", 
    "Name": "♠",
    "Load": "≥"
}

# Reverse mapping for decompression
REVREP = {v: k for k, v in REPLACEMENTS.items()}


class OutputProfiler:
    """Tracks compression statistics for the parser."""
    def __init__(self) -> None:
        self.original: int = 0
        self.compressed: int = 0

    def print(self) -> None:
        compression_ratio = (self.original - self.compressed) / self.original if self.original > 0 else 0
        print(
            f"\nCompressed AST sizes:\n"
            f"Original:                     {self.original} characters\n"
            f"Compressed:                   {self.compressed} characters\n"
            f"Compression savings:          {self.original - self.compressed} characters\n"
            f"Total compression ratio:      {compression_ratio:.1%}\n"
        )

class Parser:
    def __init__(self, filename: str) -> None:
        """
        Initialize a new Parser instance.
        """
        self.file = filename
        self.tree: Optional[ast.AST] = None
    
    @staticmethod
    def replacek(s: str, replacements: Dict[str, str]) -> str:
        """
        Replace keywords in a string with their shortened versions using regex.
        """
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, replacements.keys())) + r')\b')
        return pattern.sub(lambda x: replacements[x.group()], s)

    @staticmethod
    def unreplacek(s: str, revrep: Dict[str, str] = REVREP) -> str:
        """
        Restore shortened keywords to their original form using regex.
        """
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, revrep.keys())) + r')\b')
        return pattern.sub(lambda x: revrep[x.group()], s)
    
    def uncomp(self) -> str:
        """
        Get the uncompressed AST string representation.
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parse() yet?")
        
        return ast.dump(self.tree, indent=4)
    
    def comp(self) -> str:
        """
        Compress the AST using keyword replacement and whitespace removal.
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parse() yet?")
        
        # Remove unnecessary whitespace, attributes, and field annotations
        compast: str = ast.dump(
            self.tree, 
            annotate_fields=False, 
            include_attributes=False, 
            indent=0
        )
        
        # Remove all whitespace
        compast = "".join(compast.split())
        
        # Replace keywords with shorter versions
        compast = self.replacek(compast, REPLACEMENTS)
        
        return compast
    
    def zlibcomp(self) -> str:
        """
        Compress the AST using keyword replacement, whitespace removal, zlib, and base64 encoding.
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parse() yet?")
        
        # Minimal AST string representation
        aststr = ast.dump(
            self.tree,
            annotate_fields=False,
            include_attributes=False,
            indent=0
        )

        # Remove whitespace and apply keyword replacements
        aststr = "".join(aststr.split())
        aststr = self.replacek(aststr, REPLACEMENTS)
        
        # Compress with zlib and encode with base64
        compbytes = zlib.compress(aststr.encode('utf-8'))
        return base64.b64encode(compbytes).decode('utf-8')

    def parse(self, zlibc: bool = True) -> Tuple[str, OutputProfiler]:
        """
        Parse the source file and return its compressed representation.
        """
        profiler = OutputProfiler()

        try:
            with open(self.file, "r") as f:
                source: str = f.read()
        except FileNotFoundError:
            print(f"Error: {self.file} is not a valid file path.")
            sys.exit(1)
        except IOError as e:
            print(f"Error: Unable to read file {self.file}: {e}")
            sys.exit(1)
        
        try:
            self.tree = ast.parse(source)
        except SyntaxError as e:
            print(f"Error: Unable to parse syntax in {self.file}: {e}")
            sys.exit(1)

        # Calculate compression statistics
        profiler.original = len(self.uncomp())
        data = self.zlibcomp() if zlibc else self.comp()
        profiler.compressed = len(data)

        profiler.print()
        
        return data, profiler


if __name__ == "__main__":
    p = Parser("parser.py")
    
    print("Generating normal compression...")
    nozlib, nozlibdat = p.parse(False)
    
    print("\nGenerating zlib compression...")
    wzlib, wzlibdat = p.parse()

    print("\nCompression comparison:")
    print(f"Normal compression:  {len(nozlib)} characters")
    print(f"Zlib compression:    {len(wzlib)} characters")
    print(f"Difference:          {nozlibdat.compressed - wzlibdat.compressed} characters")
    
    print("\nNormal compression example:")
    print(nozlib[:100] + "..." if len(nozlib) > 100 else nozlib)
    
    print("\nZlib compression example:")
    print(wzlib[:100] + "..." if len(wzlib) > 100 else wzlib)
