from parser import Parser

parser = Parser("parser.py")
parser.parsefile()

print(f"ast: {parser.getuncompressed()}")

_, comp = parser.zlibcomp()
print(f"compressed: {comp}")
print("attempting to decompress")

import base64, zlib, ast
def unreplacek(s):
    replacements = {"FormattedValue": "FV", "FunctionDef": "FD", "ExceptHandler": "EX", "ImportFrom": "IF", "AnnAssign": "AA", "Attribute": "ATT", "arguments": "ARG", "Subscript": "SS", "Constant": "CO", "ClassDef": "CD", "UnaryOp": "UO", "keyword": "K", "Starred": "ST", "Return": "R", "Assign": "AS", "Import": "I", "Module": "M", "alias": "AL", "Store": "S", "value": "val", "Call": "C", "Expr": "E", "Name": "N", "Load": "L"}
    revreplacements = {v: k for k, v in replacements.items()}
    for long, short in revreplacements.items():
        s = s.replace(long, short)
    return s
compbytes = base64.b64decode(comp)
decompast = zlib.decompress(compbytes).decode('utf-8')
decompast = Parser.unreplacek(decompast)
parsedast = ast.parse(decompast)
finalast = ast.unparse(parsedast)
