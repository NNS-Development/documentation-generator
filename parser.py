from typing import Optional
from ast import dump, parse, AST, Module

def outputlen(func):
    '''returns the length of the output of a function'''
    def wrapper(*args, **kwargs):
        out = func(*args, **kwargs)
        try:
            outputlen = len(out)
        except TypeError:
            outputlen = 0
        print(f"output of {func.__name__} is {outputlen} characters long")
        return out
    return wrapper
    
class Parser:
    def __init__(self, filename: str = "") -> None:
        self.filename: str = filename
        self.tree: Optional[AST] = None
    
    def parsefile(self) -> Module:
        '''parses the file and returns the ast'''
        with open(self.filename, "r") as f:
            source: str = f.read()
        
        module: Module = parse(source)
        self.tree = module
        return self.tree
    
    @outputlen
    def getuncompressed(self) -> str:
        '''prints the ast in an uncompressed format'''
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?") # \nreport this to https://github.com/ellipticobj/documentation-generator/issues/new
        
        ast: str = dump(self.tree, indent=4)
        return ast

    @outputlen
    def getcompressed(self) -> str:
        '''
        compresses the ast as much as possible
        this is very IMPORTANT so that it uses as few tokens as possible
        '''
        if not self.tree:
            raise RuntimeError("ast is empty. have you run parsefile() yet?")
        
        compast: str = dump(self.tree, annotate_fields=False, include_attributes=False, indent=0, show_empty=False)
        return compast

if __name__ == "__main__":
    parser = Parser("parser.py") # parses itself lol funny haha
    parser.parsefile()
    uncomplen = parser.printuncompressed()
    complen = parser.getcompressed()