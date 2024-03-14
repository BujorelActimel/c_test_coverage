import os
import sys
import subprocess

def run_tests(source_file, test_file):
    # Compile the source file into an object file
    subprocess.run(["gcc", "-c", source_file])
    # Compile the test file with coverage flags and link with the object file
    subprocess.run(["gcc", "-fprofile-arcs", "-ftest-coverage", source_file, test_file, "-o", "test"])
    # Run the compiled test program
    subprocess.run(["./test"])
    # Run gcov on the source file
    subprocess.run(["gcov", f"test-{source_file}"])


def parse_gcov(source_file):
    GREEN = '\033[92m'
    RED = '\033[91m'
    NONE = '\033[0m'
    # Run gcov on the source file
    # subprocess.run(["gcov", f"test-{source_file}"])
    # Open the .gcov file
    with open(f"{source_file}.gcov", 'r') as f:
        lines = f.readlines()
    # Count the total and covered lines
    total_lines = 0
    covered_lines = 0
    for line in lines:
        line = line.strip()
        if line.startswith('#####'):
            total_lines += 1
        elif line[0].isdigit():
            total_lines += 1
            covered_lines += 1
    # Calculate and print the coverage percentage
    coverage = round(covered_lines / total_lines * 100, 2)

    if coverage > 80:
        STATUS = GREEN
    else:
        STATUS = RED

    return f"""Coverage for `{source_file}`: {STATUS}{coverage}%{NONE}
Total lines: {total_lines}
Covered lines: {STATUS}{covered_lines}{NONE}
"""


def clean_up(source_file, test_file, keep_gcov):
    if not keep_gcov:
        subprocess.run(["rm", f"{source_file}.gcov"])

    source_file = source_file.split('.')[0]
    subprocess.run(["rm", "test", f"{source_file}.o"])
    subprocess.run(["rm", f"test-{source_file}.gcda", f"test-{source_file}.gcno"])
    
    test_file = test_file.split('.')[0]
    subprocess.run(["rm", f"test-{test_file}.gcda", f"test-{test_file}.gcno"])


def clear_screen():
    os.system('clear')


def raport(files:dict, keep_gcov:bool):
    final_raport = ""
    for source_file, test_file in files.items():
        run_tests(source_file, test_file)
        final_raport += parse_gcov(source_file)
        final_raport += "\n"
        clean_up(source_file, test_file, keep_gcov)
    clear_screen()
    print(final_raport)


def main():
    source_flags = ["-source", "-s"]
    test_flags = ["-test", "-t"]
    keep_flags = ["-kg", "-keep-gcov"]
    flags = source_flags + test_flags + keep_flags
    args = sys.argv[1:]

    if len(args) < 4 or not any(flag in args for flag in source_flags) or not any(flag in args for flag in test_flags):
        print("Usage: python main.py -source/-s [source_files] -test/t [test_files] [-kg]/[keep-gcov]\nsource files should be in order relative to their test files\nExample: python main.py -s file1.c file2.c -t file1_test.c file2_test.c -kg\nNote: The source and test flags are required, the keep flag is optional\n")
        return
    
    source_files = []
    test_files = []
    keep_gcov = False

    for i in range(len(args)):
        if args[i] in source_flags:
            while i + 1 < len(args) and args[i + 1] not in flags:
                source_files.append(args[i + 1])
                i += 1
                
        elif args[i] in test_flags:
            while i + 1 < len(args) and args[i + 1] not in flags:
                test_files.append(args[i + 1])
                i += 1
        
        elif args[i] in keep_flags:
            keep_gcov = True

    files = {}
    for i in range(len(source_files)):
        files[source_files[i]] = test_files[i]

    # print(f"Source files: {source_files}")
    # print(f"Test files: {test_files}")
    # print(f"Keep gcov files: {keep_gcov}")
    # print(files)

    raport(files, keep_gcov)


if __name__ == "__main__":
    main()
