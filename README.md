# Code Coverage Tool

This is a Python-based tool for calculating code coverage of C programs. It uses `gcov` and `gcc` to compile and analyze the code. The tool provides a percentage of code coverage, total lines of code, and the number of lines covered.

## Usage

To use this tool, you need to pass the source files and their corresponding test files as command-line arguments. The source and test files should be in the same order. 

Here is an example of how to use the tool:

```sh
python main.py -s module.c mod2/module2.c -t test_module.c mod2/test_module2.c
```

In this example, module.c and mod2/module2.c are the source files, and test_module.c and mod2/test_module2.c are their corresponding test files.

You can also use the -kg or -keep-gcov flag to keep the .gcov files generated during the analysis:

```sh
python main.py -s module.c mod2/module2.c -t test_module.c mod2/test_module2.c -kg
```

## Requirements
- unix based os (for now)
- Python 3
- gcc
- gcov

```Note
This tool assumes that the source files and test files are in the same directory (for Now)
```