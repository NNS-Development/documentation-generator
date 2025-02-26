import ast
import zlib
import base64
from typing import Optional, Tuple

    
class OutputProfiler:
    '''tracks compression stats'''
    def __init__(self):
        self.original = 0
        self.compressed = 0

    def print(self):
        """Generate compression performance report"""
        return (
        f"""
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
    def unreplacek(s: str) -> str:
        '''
        replaces shortened characters with original keywords
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
        
        revreplacements = {v: k for k, v in replacements.items()}
    
        # unreplaces
        for long, short in revreplacements.items():
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
        # removes unnecessary whitespace and attributes (decreases length of output by ~71%)
        compast: str = ast.dump(self.tree, annotate_fields=False, include_attributes=False, indent=0)
        
        # remove newlines + whitespace (decreases length by ~7%)
        compast = "".join(compast.split())
        
        # replace keywords with shorter versions (decreases length by ~40%)
        compast = self.replacek(compast)
        
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
        # no whitespace
        aststr = "".join(aststr.split())
        
        # replace keywords with shorter versions (decreases length by ~40%)
        aststr = self.replacek(aststr)
        
        # base64 compressed bytes
        compbytes = zlib.compress(aststr.encode('utf-8'))
        encstr = base64.b64encode(compbytes).decode('utf-8')
        
        return encstr

    def parse(self, zlibc: bool = True) -> Tuple[str, OutputProfiler]:
        '''entry point'''
        profiler = OutputProfiler()

        with open(self.file, "r") as f:
            source: str = f.read()
        
        self.tree = ast.parse(source)

        profiler.original = len(self.uncomp())

        if zlibc:
            data = self.zlibcomp()
        else:
            data = self.comp()

        profiler.compressed = len(data)

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