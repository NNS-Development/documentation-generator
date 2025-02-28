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

REPLACEMENTS = {
    "FormattedValue": "♦",
    "FunctionDef": "♥",
    "ExceptHandler": "♣",
    "ImportFrom": "♠",
    "AnnAssign": "●",
    "Attribute": "■",
    "arguments": "▲",
    "Subscript": "◆",
    "Constant": "★",
    "ClassDef": "✦",
    "UnaryOp": "►",
    "keyword": "«",
    "Starred": "»",
    "Return": "✓",
    "Assign": "⌂",
    "Import": "⌘",
    "Module": "⊕",
    "alias": "⊗",
    "Store": "⊠",
    "value": "⊡",
    "Call": "⊢",
    "Expr": "⊣",
    "Name": "⋄",
    "Load": "⋆"
}

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
        
        # minimal ast
        compast: str = ast.dump(
            self.tree, 
            annotate_fields=False, 
            include_attributes=False, 
            indent=0
        )
        
        # remove all whitespace
        compast = "".join(compast.split())
        
        # replace keywords with symbols
        compast = self.replacek(compast, REPLACEMENTS)
        
        return compast
    
    @staticmethod
    def decompress(compressed: str, is_zlib: bool = True) -> str:
        """
        Decompress an AST representation that was previously compressed.
        """
        if is_zlib:
            try:
                decoded = base64.b64decode(compressed)
                decompressed = zlib.decompress(decoded).decode('utf-8')
            except Exception as e:
                raise ValueError(f"Failed to decompress data: {e}")
        else:
            decompressed = compressed
            
        return Parser.unreplacek(decompressed)
    
    def zlibcomp(self) -> str:
        """
        Compress the AST using keyword replacement, whitespace removal, zlib, and base64 encoding.
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parse() yet?")
        
        # minimal ast
        aststr = ast.dump(
            self.tree,
            annotate_fields=False,
            include_attributes=False,
            indent=0
        )

        aststr = "".join(aststr.split())
        aststr = self.replacek(aststr, REPLACEMENTS)
        
        # compress
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

        # stats
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

    compr = wzlib
    try:
        decompressed = Parser.decompress(compr)
        print("Compression/decompression compatibility test successful")
        # Optionally print a small part of the decompressed string to verify
        print(decompressed[:100] + "..." if len(decompressed) > 100 else decompressed)
    except Exception as e:
        print(f"Compatibility test failed: {e}")
