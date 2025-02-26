import ast
import zlib
import base64
from typing import Optional, Tuple, Dict

REPLACEMENTS = {
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
REVREP = {v: k for k, v in REPLACEMENTS.items()}

class OutputProfiler:
    '''tracks compression stats'''
    def __init__(self):
        self.original = 0
        self.compressed = 0

    def print(self):
        """Generate compression performance report"""
        return (
        f"""
Compressed AST sizes:
Original:                     {self.original} characters
Compressed:                   {self.compressed} characters
Compression savings:          {self.original-self.compressed} characters
Total compression ratio:      {(self.original-self.compressed)/self.original:.1%}"""
        )

class Parser:
    def __init__(self, filename) -> None:
        self.file = filename
        self.tree: Optional[ast.AST] = None
    
    @staticmethod
    def replacek(s: str, replacements: Dict[str, str]) -> str:
        '''replaces keywords with shortened characters'''
        for long, short in replacements.items():
            s = s.replace(long, short)
        return s
    
    @staticmethod
    def unreplacek(s: str, revrep: Dict[str, str]=REVREP) -> str:
        '''replaces shortened characters with original keywords'''
        for long, short in revrep.items():
            s = s.replace(long, short)
        return s
    
    def uncomp(self) -> str:
        '''prints the ast in an uncompressed format'''
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?")
        
        aststr: str = ast.dump(self.tree, indent=4)

        return aststr
    
    def comp(self) -> str:
        '''
        compresses the ast as much as possible without zlib
        '''
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?")
        
        # ballpark figures lol
        compast: str = ast.dump(self.tree, annotate_fields=False, include_attributes=False, indent=0) # removes unnecessary whitespace and attributes (decreases length of output by ~71%)
        compast = "".join(compast.split()) # remove newlines + whitespace (decreases length by ~7%)
        compast = self.replacek(compast, REPLACEMENTS) # replace keywords with shorter versions (decreases length by ~40%)
        
        return compast
    
    def zlibcomp(self) -> str:
        """
        compresses the ast, then compresses it again using zlib
        """
        if not self.tree:
            raise RuntimeError("AST is empty. Have you run parsefile() yet?")
        
        # minimal formatting
        aststr = ast.dump(
            self.tree,
            annotate_fields=False,
            include_attributes=False,
            indent=0
        )

        aststr = "".join(aststr.split()) # no whitespace
        aststr = self.replacek(aststr, REPLACEMENTS) # replace keywords with shorter versions (decreases length by ~40%)
        compbytes = zlib.compress(aststr.encode('utf-8')) # compress using zlib
        encstr = base64.b64encode(compbytes).decode('utf-8') # base64 compressed bytes
        
        return encstr

    def parse(self, zlibc: bool = True) -> Tuple[str, OutputProfiler]:
        '''entry point'''
        profiler = OutputProfiler()

        with open(self.file, "r") as f:
            source: str = f.read()
        
        self.tree = ast.parse(source) # get the ast
        profiler.original = len(self.uncomp()) # get the original tree's length
        data = self.zlibcomp() if zlibc else self.comp() # use appropriate compression type
        profiler.compressed = len(data) # set compressed length

        print(profiler.print())

        return data, profiler
    
if __name__ == "__main__":
    p = Parser("parser.py")
    nozlib, nozlibdat = p.parse(False)
    wzlib, wzlibdat = p.parse()

    print("normal compression: ")
    print(nozlib)
    print()
    print("zlib compressed: ")
    print(wzlib)
    print()
    print("normal compression data: ", end="")
    print(nozlibdat.print())
    print()
    print("zlib compressed data: ", end="")
    print(wzlibdat.print())
    print()
    print(f"difference: {nozlibdat.compressed-wzlibdat.compressed}")