# CCOV

This is a Python-based tool for calculating code coverage of C programs. It uses `gcov` and `gcc` to compile and analyze the code. The tool provides a percentage of code coverage, total lines of code, and the number of lines covered.

## Usage

To use this tool, you need to pass the path to a source file and it's corresponding test file as command-line arguments.

Here is an example of how to use the tool:

```bash
python main.py path/to/module.c path/to/test_module.c
```

In this example, module.c is the source file, and test_module.c is the corresponding test file.

You can also use the --keep-gcov flag to keep the .gcov files generated during the analysis:

```bash
python main.py --keep-gcov path/to/module.c path/to/test_module.c
```

## Requirements
- unix based os (If you are a Windows user it is highly recommended to use WSL)
- Python 3
- gcc
- gcov
- Python packages: typer, rich, typing_extensions (These can be installed using pip install -r requirements.txt)
