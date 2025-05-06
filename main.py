#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import tempfile

def compile_cpp(file_path, output_name):
    """Compile C++ file and return the path to the executable."""
    try:
        subprocess.run(
            ["g++-14", "-std=c++17", "-O2", file_path, "-o", output_name],
            check=True,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {file_path}: {e.stderr.decode()}")
        return False

def run_generator(n, m, t, max_w=None):
    """Run the generator and return the generated graph as a string."""
    cmd = ["python3", "generator.py", str(n), str(m), str(t)]
    if max_w is not None:
        cmd.append(str(max_w))
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def run_t_spanner(input_graph):
    """Run t-spanner algorithm on the input graph and return the output."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(input_graph)
        tmp_name = tmp.name

    result = subprocess.run(
        ["./t_spanner_exec"],
        input=input_graph,
        capture_output=True,
        text=True
    )
    
    return result.stdout

def run_checker(original_graph, spanner_output):
    """Run the checker to verify if the spanner is valid."""
    combined_input = original_graph + spanner_output
    result = subprocess.run(
        ["./checker_exec"],
        input=combined_input,
        capture_output=True,
        text=True
    )
    
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="T-Spanner Test Framework")
    parser.add_argument("test_cases", type=int, help="Number of test cases to run")
    parser.add_argument("--n", type=int, default=10, help="Number of vertices (default: 10)")
    parser.add_argument("--m", type=int, default=None, help="Number of edges (default: n^2/2)")
    parser.add_argument("--t", type=int, default=3, help="T parameter for spanner (default: 3)")
    parser.add_argument("--max_w", type=int, default=None, help="Maximum edge weight (default: n)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed outputs")
    
    args = parser.parse_args()
    
    # Compile the C++ executables
    if not compile_cpp("algo/t-spanner.cpp", "t_spanner_exec"):
        print("Failed to compile t-spanner.cpp")
        return
    
    if not compile_cpp("checker.cpp", "checker_exec"):
        print("Failed to compile checker.cpp")
        return
    
    print(f"Running {args.test_cases} test cases with n={args.n}, t={args.t}")
    
    successful_cases = 0
    for i in range(args.test_cases):
        print(f"\nTest case {i+1}/{args.test_cases}:")
        
        # Generate random graph
        original_graph = run_generator(args.n, args.m, args.t, args.max_w)
        if args.verbose:
            print("Original graph:")
            print(original_graph)
        
        # Run t-spanner algorithm
        spanner_output = run_t_spanner(original_graph)
        if args.verbose:
            print("T-spanner output:")
            print(spanner_output)
        
        # Verify using checker
        result = run_checker(original_graph, spanner_output)
        is_valid = result == "YES"
        
        if is_valid:
            successful_cases += 1
            print(f"✅ Test case {i+1}: Valid t-spanner")
        else:
            print(f"❌ Test case {i+1}: Invalid t-spanner")
        
        if args.verbose:
            print(f"Checker output: {result}")
    
    print(f"\nSummary: {successful_cases}/{args.test_cases} valid t-spanners")

if __name__ == "__main__":
    main()