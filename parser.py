from astroid import parse, Module

class Parser:
    def __init__(self, filename: str = ""):
        self.filename: str = filename
        self.tree: Module = None
    
    def parse(self):
        with open(self.filename, "r") as f:
            self.tree = parse(f.read())
