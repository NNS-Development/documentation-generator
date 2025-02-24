# documentation generator for python (for now)
this is an automatic documentation generator using generative ai made in python.  
this should not be used in production-ready apps. it is not a replacement for actual humans.  

## IMPORTANT NOTES
this CAN use a HUGE amount of tokens if your codebase is big. PLEASE PLEASE DO NOT use this on actual projects.   
this is just a proof of concept and is NOT a finalized product.  

## how do i use this?
its current in development, so you cannot use it :3  
soon though.  

## what does this do?
this aims to give users a fast and easy way to generate docstrings/documentation for their python programs (for now only python)

## how does it work?
it uses python's [ast](https://docs.python.org/3/library/ast.html) module to parse the code into an ast, then processes it using google gemini's api key to generate a suitable summary of the code.

## development progress
using [test.py](test.py) generates [documentation.md](documentation.md), which used:
Prompt tokens: 1430
Response tokens: 1318
Total tokens: 2748

### completed
code parser
data compression
basic ai prompt


### in progress
ai analyzer

### planned features
multi file support
docstring detection + analyzing  
ai integration  
github actions support (for things like auto docuentations on push)

<!-- future?
 # Intelligent Natural Language Code Documentation Generator
Develop a tool that automatically generates and updates human-readable documentation from codebases using advanced NLP techniques.

## core technologies: 
transformer-based NLP models (like GPT or BERT variants), code parsing and static analysis, and summarization algorithms.

## key features: 
Context-aware documentation, continuous integration with code repositories, and multi-language support for various programming languages (planned).

## how it works -->
