from astroid import parse, Module

class Parser:
    def __init__(self, filename: str = "") -> None:
        self.filename: str = filename
        self.tree: Module = None
    
    def parsefile(self) -> Module:
        with open(self.filename, "r") as f:
            source: str = f.read()
        
        module: Module = parse(source)
        return module
    
    def parse(self) -> Module:
        if self.tree is None:
            self.tree = self.parsefile()
        
        return self.tree
    
    def print_nodes(self) -> None:
        if self.tree is None:
            self.tree = self.parsefile()
        
        for node in self.tree.get_children():
            print(node)    

if __name__ == "__main__":
    parser = Parser("parser.py") # parses itself lol funny haha
    parser.print_nodes()
