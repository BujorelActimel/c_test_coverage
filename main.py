from pathlib import Path
from typing import List
from typing_extensions import Annotated
from rich.progress import Progress, TextColumn, BarColumn


import os
import typer
import subprocess


def check_imports(file: Path) -> int:
    libs = 0

    with open(file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith("#include") and line.split()[1].startswith('"'):
            libs += 1
    return libs


def run_tests(source_file: Path, test_file: Path):
    if not source_file.exists():
        typer.secho(f"Source file `{source_file}` does not exist", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
    
    if not test_file.exists():
        typer.secho(f"Test file `{test_file}` does not exist", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
    
    source_imports = check_imports(source_file)
    test_imports = check_imports(test_file)

    file_name = os.path.basename(source_file)
    # Compile the source file into an object file
    subprocess.run(["gcc", "-c", source_file])

    try:
        files_to_compile = set()
        files_to_compile.add(source_file)
        files_to_compile.add(test_file)

        files_to_compile = list(files_to_compile)
        # Compile the test file with coverage flags and link with the object file
        subprocess.run(["gcc", "-fprofile-arcs", "-ftest-coverage", *files_to_compile, "-o", "test"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # Run the compiled test program
        subprocess.run(["./test"])
        # Run gcov on the source file
        subprocess.run(["gcov", f"test-{file_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    except:
        clean_up(source_file, test_file, False)

        files_to_compile = set()
        files_to_compile.add(source_file)
        files_to_compile.add(test_file)

        if source_imports and test_imports:
            if typer.confirm(f"There are {source_imports  + test_imports} missing imports from {source_file} and {test_file}. Do you want to continue?"):
                paths_to_import = list(map(Path, typer.prompt("Enter the files that need to be imported").split()))

        elif source_imports:
            if typer.confirm(f"Source file `{source_file}` has {source_imports} imports. Do you want to continue?"):
                paths_to_import += list(map(Path, typer.prompt("Enter the files that need to be imported").split()))

        elif test_imports:
            if typer.confirm(f"Test file `{test_file}` has {test_imports} imports. Do you want to continue?"):
                paths_to_import += list(map(Path, typer.prompt("Enter the files that need to be imported").split()))


        for file in paths_to_import:
            if file.exists():
                files_to_compile.add(file)
        
        files_to_compile = list(files_to_compile)
        # Compile the test file with coverage flags and link with the object file
        subprocess.run(["gcc", "-fprofile-arcs", "-ftest-coverage", *files_to_compile, "-o", "test"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # Run the compiled test program
        subprocess.run(["./test"])
        # Run gcov on the source file
        subprocess.run(["gcov", f"test-{file_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def coverage_results(source_file: Path) -> tuple[int, int, float]:
    file_name = os.path.basename(source_file)

    with open(f"{file_name}.gcov", 'r') as f:
        lines = f.readlines()

    total_lines = 0
    covered_lines = 0

    for line in lines:
        line = line.strip()
        if line.startswith('#####'):
            total_lines += 1
        elif line[0].isdigit():
            total_lines += 1
            covered_lines += 1

    coverage = round(covered_lines / total_lines * 100, 2)

    return total_lines, covered_lines, coverage


def clean_up(source_file: Path, test_file: Path, keep_gcov: bool):
    file_name = os.path.basename(source_file)
    
    all_files = [f for f in os.listdir('.') if os.path.isfile(f)]

    for f in all_files:
        if f.startswith("test-") and (f.endswith(".gcda") or f.endswith(".gcno")):
            subprocess.run(["rm", f])

    if not keep_gcov and Path(f"{file_name}.gcov").exists():
        subprocess.run(["rm", f"{file_name}.gcov"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    file_name = file_name.split('.')[0]
    if Path(f"{file_name}.o").exists():
        subprocess.run(["rm", f"{file_name}.o"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    if Path("test").exists():
        subprocess.run(["rm", "test"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def main(source_file: Path, test_file: Path, keep_gcov: bool = False):
    """
    Run tests and calculate coverage for a C source file.
    """
    try:
        run_tests(source_file, test_file)
    except:
        typer.secho("Error running tests", fg=typer.colors.RED, bold=True)
        clean_up(source_file, test_file, False)
        return
    
    total_lines, covered_lines, coverage = coverage_results(source_file)

    if coverage < 80:
        color = typer.colors.RED
    else:
        color = typer.colors.GREEN

    typer.secho(f"Coverage for `{source_file}`: {coverage}%\n{covered_lines}/{total_lines} lines covered", fg=color, bold=True)

    with Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=None, complete_style=typer.colors.GREEN, finished_style=typer.colors.GREEN),
        TextColumn("{task.completed}%"),
    ) as progress:
        task_id = progress.add_task("", total=100)
        progress.update(task_id, completed=coverage)
    
    clean_up(source_file, test_file, keep_gcov)


if __name__ == "__main__":
    typer.run(main)
