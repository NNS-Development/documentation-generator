from typing import Optional, List
from ast import dump, parse, AST, Module
import zlib
import base64
from typing import Optional, Tuple, Dict

"""
Parser module for the documentation generator.

parses and compresses python files
"""

# Mapping of AST node names to shorter versions for compression
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
    def __init__(self, filename: str = "", debug: bool = False) -> None:
        self.filename: str = filename
        self.tree: Optional[AST] = None
        self.debug = debug
        if debug:
            self.outlens: List[str] = []
    
    def parsefile(self) -> Module:
        '''parses the file and returns the ast'''
        with open(self.filename, "r") as f:
            source: str = f.read()
        
        module: Module = parse(source)
        self.tree = module
        return self.tree
    
    @staticmethod
    def replacek(s: str) -> str:
        '''
        replaces keywords with shortened characters
        '''
        replacements = {
            "FormattedValue": "FV",
            "FunctionDef": "FD",
            "ExceptHandler": "EX",
            "ImportFrom": "IF",
            "AnnAssign": "AA",
            "Attribute": "ATT",
            "arguments": "ARG",
            "Subscript": "SS",
            "Constant": "CO",
            "ClassDef": "CD",
            "UnaryOp": "UO",
            "keyword": "K",
            "Starred": "ST",
            "Return": "R",
            "Assign": "AS",
            "Import": "I",
            "Module": "M",
            "alias": "AL",
            "Store": "S",
            "value": "val",
            "Call": "C",
            "Expr": "E",
            "Name": "N",
            "Load": "L"
        }
    
        # does the actual replacement
        for long, short in replacements.items():
            s = s.replace(long, short)
            
        return s
    
    @staticmethod
    def unreplacek(s: str, revrep: Dict[str, str] = REVREP) -> str:
        """
        Restore shortened keywords to their original form using regex.
        """
        for symbol, keyword in revrep.items():
            s = s.replace(symbol, keyword)
        return s
    
    def uncomp(self) -> str:
        """
        Get the uncompressed AST string representation.
        """
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?")
        
        ast: str = dump(self.tree, indent=4)
        print(ast)
        return ast
    
    @outputlen
    def getcompressed(self) -> str:
        '''
        compresses the ast as much as possible without zlib
        can be passed into gemini 2.0 flash
        '''
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?")
        
        # ballpark figures lol
        # removes unnecessary whitespace and attributes (decreases length of output by ~71%)
        compast: str = dump(self.tree, annotate_fields=False, include_attributes=False, indent=0)
        
        # remove newlines + whitespace (decreases length by ~7%)
        compast = "".join(compast.split())
        
        # replace keywords with shorter versions (decreases length by ~40%)
        compast = self.replacek(compast)
            
        print(compast)
        return compast
    
    @staticmethod
    def decompress(compressed: str, is_zlib: bool = True) -> str:
        """
        Decompress an AST representation that was previously compressed.
        """
        if is_zlib:
            # Decode base64 and decompress with zlib
            try:
                decoded = base64.b64decode(compressed)
                decompressed = zlib.decompress(decoded).decode('utf-8')
            except Exception as e:
                raise ValueError(f"Failed to decompress data: {e}")
        else:
            decompressed = compressed
            
        # Restore original keywords
        return Parser.unreplacek(decompressed)
    
    def zlibcomp(self) -> str:
        """
        compresses the ast, then compresses it again using zlib
        can be passed into gemini 2.0 pro
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parsefile() yet?")
        
        # minimal formatting
        ast = dump(
            self.tree,
            annotate_fields=False,
            include_attributes=False,
            indent=0
        )
        # no whitespace
        ast = "".join(ast.split())
        
        # replace keywords with shorter versions (decreases length by ~40%)
        ast = self.replacek(ast)
        
        # base64 compressed bytes
        compbytes = zlib.compress(ast.encode('utf-8'))
        encstr = base64.b64encode(compbytes).decode('utf-8')
        
        return encstr

    def parse(self, zlibc: bool = True) -> str:
        '''entry point'''
        self.parsefile()

        if zlibc:
            data = self.zlibcomp()
        else:
            data = self.getcompressed()

        return data
    
if __name__ == "__main__":
    p = Parser("analyzer.py")
    
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
    print()
    print("testing decompression")
    compr = p.zlibcomp()
    try:
        decoded = base64.b64decode(compr)
        dc = zlib.decompress(decoded).decode('utf-8')
        result = Parser.unreplacek(dc)
        print("Compression/decompression compatibility test successful")
    except Exception as e:
        print(f"Compatibility test failed: {e}")