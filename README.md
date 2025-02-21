# documentation generator for python (for now)
this is an automatic documentation generator using generative ai made in python.  
this should not be usediin production-ready apps. it is not a replacement for actual humans.  

## what does this do?
this aims to give users a fast and easy way to generate docstrings/documentation for their python programs

## how does it work?
it uses python's [asteroid](https://pypi.org/project/astroid/) module to parse the code into an ast, then processes it using google gemini's api key to generate a suitable summary of the code.

## development progres

### in progress
code parser (data compression)

### planned features
multi file
docstring detection  
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