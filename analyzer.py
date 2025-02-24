"""
analyer.py

get the encoded string from parser.py using Parser.zlibcomp()
pass it using the code i put in analyzer.py for realsies
magic
analyzer finished ong
"""
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-pro-exp-02-05",
    generation_config=generation_config,
    system_instruction="you will be given a string. this string has been compressed. you can decompress it using this script \"import base64, zlib, ast\ndef unreplacek(s):\n    replacements = {\"FormattedValue\": \"FV\", \"FunctionDef\": \"FD\", \"ExceptHandler\": \"EX\", \"ImportFrom\": \"IF\", \"AnnAssign\": \"AA\", \"Attribute\": \"ATT\", \"arguments\": \"ARG\", \"Subscript\": \"SS\", \"Constant\": \"CO\", \"ClassDef\": \"CD\", \"UnaryOp\": \"UO\", \"keyword\": \"K\", \"Starred\": \"ST\", \"Return\": \"R\", \"Assign\": \"AS\", \"Import\": \"I\", \"Module\": \"M\", \"alias\": \"AL\", \"Store\": \"S\", \"value\": \"val\", \"Call\": \"C\", \"Expr\": \"E\", \"Name\": \"N\", \"Load\": \"L\"}\n    revreplacements = {v: k for k, v in replacements.items()}\n    for long, short in revreplacements.items():\n        s = s.replace(long, short)\n    return s\nfinalast = ast.unparse(ast.parse(unreplacek(zlib.decompress(base64.b64decode(comp)).decode('utf-8'))))\"\nhelp me analyze finalast, which should be an abstract syntax tree for a python script, and provide detailed documentation for it in markdown format. ",
    tools='code_execution',
)

chat_session = model.start_chat()