#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import tempfile
import matplotlib.pyplot as plt
import numpy as np

def compile_cpp(file_path, output_name):
    """Compile C++ file and return the path to the executable."""
    try:
        compiler = "g++-14" if sys.platform == "darwin" else "g++"
        subprocess.run(
            [compiler, "-std=c++17", "-O2", file_path, "-o", output_name],
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
    # Check if the output is empty or invalid
    output = result.stdout
    if not output.strip():
        print("Warning: Generator produced empty output!")
        return None
    
    # Verify the output contains valid graph data
    lines = output.strip().split('\n')
    if len(lines) < 1:
        print("Warning: Generator output has insufficient lines!")
        return None
    
    try:
        # Check if first line has the format "n m t"
        params = lines[0].split()
        if len(params) != 3:
            print(f"Warning: Invalid first line format: {lines[0]}")
            return None
            
        n_out, m_out, t_out = map(int, params)
        
        # Check if we have enough edge lines
        if len(lines) != m_out + 1:
            print(f"Warning: Expected {m_out + 1} lines, got {len(lines)}")
    except ValueError:
        print(f"Warning: Invalid number format in generator output")
        return None
    
    return output

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

def run_t_spanner_with_timing(input_graph):
    """Run t-spanner algorithm and return output and timing information."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(input_graph)
        tmp_name = tmp.name

    result = subprocess.run(
        ["./t_spanner_exec"],
        input=input_graph,
        capture_output=True,
        text=True
    )
    
    # Extract timing information from stderr
    timing_info = {}
    stderr_lines = result.stderr.strip().split('\n')
    if len(stderr_lines) >= 3:  # Expecting phase1, phase2, and total timings
        try:
            timing_info['phase1'] = int(stderr_lines[0])
            timing_info['phase2'] = int(stderr_lines[1])
            timing_info['total'] = int(stderr_lines[2])
        except (ValueError, IndexError):
            pass
    
    return result.stdout, timing_info

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

def parse_graph_info(graph_str):
    """Parse the graph string to extract n and m."""
    if not graph_str:
        return None, None
    
    lines = graph_str.strip().split('\n')
    if not lines:
        return None, None
    
    try:
        params = lines[0].split()
        # if len(params) != 3:
        #     return None, None
        
        n, m = map(int, params[:2])
        return n, m
    except (ValueError, IndexError):
        return None, None

def plot_edge_comparison(n_values, original_m_values, spanner_m_values, t):
    """Plot a comparison of original and spanner edge counts."""
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, original_m_values, 'b-o', label='Original Graph Edges')
    plt.plot(n_values, spanner_m_values, 'r-o', label='T-Spanner Edges')
    
    plt.xlabel('Number of Vertices (n)')
    plt.ylabel('Number of Edges (m)')
    plt.title(f'Comparison of Edge Counts between Original Graph and {t}-Spanner')
    plt.legend()
    plt.grid(True)
    
    # Add annotations for the edge reduction percentage
    if len(n_values) <= 10:
        for i in range(len(n_values)):
            if original_m_values[i] > 0:
                reduction = 100 * (1 - spanner_m_values[i] / original_m_values[i])
                plt.annotate(f"{reduction:.1f}%", 
                            xy=(n_values[i], (original_m_values[i] + spanner_m_values[i])/2),
                            xytext=(5, 0), 
                            textcoords='offset points')
    
    # Create plots directory if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    
    # Include t in the filename
    filename = f'plots/edge_comparison_t{t}.png'
    plt.savefig(filename)
    print(f"Plot saved to '{filename}'")
    plt.show()

def plot_time_comparison(n_values, time_values_by_t, title):
    """Plot a comparison of time taken for different t values."""
    plt.figure(figsize=(12, 7))
    
    for t, time_data in time_values_by_t.items():
        plt.plot(n_values, time_data, marker='o', linewidth=2, label=f't={t}')
    
    plt.xlabel('Number of Vertices (n)')
    plt.ylabel('Time (microseconds)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    
    # Use log scale if values span multiple orders of magnitude
    if max(max(times) for times in time_values_by_t.values()) > 1000:
        plt.yscale('log')
    
    # Create plots directory if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    
    # Generate filename based on title
    safe_title = title.lower().replace(' ', '_')
    filename = f'plots/{safe_title}.png'
    plt.savefig(filename)
    print(f"Plot saved to '{filename}'")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="T-Spanner Test Framework")
    parser.add_argument("--test_cases", type=int, nargs="?", default=1, help="Number of test cases to run per n value")
    parser.add_argument("--n", type=int, default=10, help="Number of vertices (default: 10)")
    parser.add_argument("--m", type=int, default=None, help="Number of edges (default: n^2/2)")
    parser.add_argument("--t", type=int, default=3, help="T parameter for spanner (default: 3)")
    parser.add_argument("--max_w", type=int, default=None, help="Maximum edge weight (default: n)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed outputs")
    
    # Add plot parameters
    parser.add_argument("--plot", action="store_true", help="Generate comparison plot")
    parser.add_argument("--plot_weights", action="store_true", help="Generate weight comparison plot")
    parser.add_argument("--min_n", type=int, default=10, help="Minimum n value for plotting")
    parser.add_argument("--max_n", type=int, default=100, help="Maximum n value for plotting")
    parser.add_argument("--growth_factor", type=float, default=None, help="Multiply n by this factor for each step")
    parser.add_argument("--addition_factor", type=int, default=None, help="Add this value to n for each step")
    parser.add_argument("--steps", type=int, default=10, help="Number of steps between min_n and max_n (used if neither growth nor addition factor is specified)")
    parser.add_argument("--plot_min_w", type=int, default=1, help="Minimum edge weight for weight comparison plot")
    parser.add_argument("--plot_max_w", type=int, default=100, help="Maximum edge weight for weight comparison plot")
    parser.add_argument("--t_values", type=int, nargs="*", help="List of t values for weight comparison plot")
    
    # Add time analysis option
    parser.add_argument("--plot_time", action="store_true", help="Generate time analysis plot")
    
    args = parser.parse_args()

    # Compile the C++ executables
    if not compile_cpp("algo/t-spanner.cpp", "t_spanner_exec"):
        print("Failed to compile t-spanner.cpp")
        return
    
    if not compile_cpp("checker.cpp", "checker_exec"):
        print("Failed to compile checker.cpp")
        return
    
    if args.plot_weights:
        # Generate a sequence of max_w values
        w_values = []
        if args.steps:
            w_values = [int(w) for w in np.linspace(args.plot_min_w, args.plot_max_w, args.steps)]
        else:
            # Default to 10 steps if not specified
            w_values = [int(w) for w in np.linspace(args.plot_min_w, args.plot_max_w, 10)]
        
        t_values = args.t_values if args.t_values else [3, 5, 7]
        n = args.n
        
        plt.figure(figsize=(10, 6))
        
        for t in t_values:
            spanner_edges_by_weight = []
            
            for max_w in w_values:
                print(f"\nTesting with n={n}, t={t}, max_w={max_w}")
                
                # For each weight, run multiple test cases and take the average
                spanner_edges = []
                
                for i in range(args.test_cases):
                    # Calculate m based on n if not specified
                    m = args.m if args.m is not None else n * (n - 1) // 2
                    
                    # Generate graph and run algorithm
                    original_graph = run_generator(n, m, t, max_w)
                    if not original_graph:
                        continue
                    
                    spanner_output = run_t_spanner(original_graph)
                    if not spanner_output:
                        continue
                    
                    # Extract edge count
                    _, spanner_m = parse_graph_info(spanner_output)
                    
                    if spanner_m is not None:
                        spanner_edges.append(spanner_m)
                        
                    # Check if spanner is valid
                    result = run_checker(original_graph, spanner_output)
                    is_valid = result == "YES"
                    print(f"  Test case {i+1}: {'Valid' if is_valid else 'Invalid'} t-spanner")
                
                if spanner_edges:
                    avg_spanner_m = sum(spanner_edges) / len(spanner_edges)
                    spanner_edges_by_weight.append(avg_spanner_m)
                    print(f"  Average spanner edges: {avg_spanner_m:.1f}")
                else:
                    print(f"  No valid data for max_w={max_w}")
                    spanner_edges_by_weight.append(None)
            
            # Plot the line for this t value
            plt.plot(w_values, spanner_edges_by_weight, marker='o', label=f't={t}')
        
        plt.xlabel('Maximum Edge Weight')
        plt.ylabel('Number of Edges in t-Spanner')
        plt.title(f'Effect of Edge Weight on Spanner Size (n={n})')
        plt.legend()
        plt.grid(True)
        
        # Create plots directory if it doesn't exist
        os.makedirs('plots', exist_ok=True)
        
        filename = f'plots/weight_comparison_n{n}.png'
        plt.savefig(filename)
        print(f"Plot saved to '{filename}'")
        plt.show()
    
    elif args.plot:
        # Generate a sequence of n values based on growth or addition factor
        n_values = []
        
        if args.growth_factor is not None and args.addition_factor is not None:
            print("Warning: Both growth_factor and addition_factor provided. Using growth_factor.")
            n = args.min_n
            while n <= args.max_n:
                n_values.append(int(n))
                n *= args.growth_factor
        elif args.growth_factor is not None:
            # Geometric progression
            n = args.min_n
            while n <= args.max_n:
                n_values.append(int(n))
                n *= args.growth_factor
        elif args.addition_factor is not None:
            # Arithmetic progression
            n = args.min_n
            while n <= args.max_n:
                n_values.append(int(n))
                n += args.addition_factor
        else:
            # Linear spacing between min_n and max_n
            n_values = [int(n) for n in np.linspace(args.min_n, args.max_n, args.steps)]
        
        original_m_values = []
        spanner_m_values = []
        
        for n in n_values:
            print(f"\nTesting with n={n}")
            
            # For each n, run multiple test cases and take the average
            orig_edges = []
            spanner_edges = []
            
            for i in range(args.test_cases):
                # Calculate m based on n if not specified
                m = args.m if args.m is not None else n * (n - 1) // 2
                max_w = args.max_w if args.max_w is not None else n
                
                # Generate graph and run algorithm
                original_graph = run_generator(n, m, args.t, max_w)
                if not original_graph:
                    continue
                
                spanner_output = run_t_spanner(original_graph)
                if not spanner_output:
                    continue
                
                # Extract edge counts
                _, orig_m = parse_graph_info(original_graph)
                _, spanner_m = parse_graph_info(spanner_output)
                
                if orig_m is not None and spanner_m is not None:
                    orig_edges.append(orig_m)
                    spanner_edges.append(spanner_m)
                    
                # Check if spanner is valid
                result = run_checker(original_graph, spanner_output)
                is_valid = result == "YES"
                print(f"  Test case {i+1}: {'Valid' if is_valid else 'Invalid'} t-spanner")
                
            if orig_edges and spanner_edges:
                avg_orig_m = sum(orig_edges) / len(orig_edges)
                avg_spanner_m = sum(spanner_edges) / len(spanner_edges)
                
                original_m_values.append(avg_orig_m)
                spanner_m_values.append(avg_spanner_m)
                
                print(f"  Average edges - Original: {avg_orig_m:.1f}, T-Spanner: {avg_spanner_m:.1f}")
            else:
                print(f"  No valid data for n={n}")
        
        if original_m_values and spanner_m_values:
            plot_edge_comparison(n_values, original_m_values, spanner_m_values, args.t)
        else:
            print("No data to plot. Try different parameters or check for errors ")        
    
    elif args.plot_time:
        # Generate a sequence of n values
        n_values = [int(n) for n in np.linspace(args.min_n, args.max_n, args.steps)]
        
        # Use provided t_values or default
        t_values = args.t_values if args.t_values else [3, 5, 7]
        
        # Dictionary to store timing data for each t value
        phase1_times = {t: [] for t in t_values}
        phase2_times = {t: [] for t in t_values}
        total_times = {t: [] for t in t_values}
        
        for n in n_values:
            print(f"\nTesting with n={n}")
            
            for t in t_values:
                print(f"  Running with t={t}")
                
                # Calculate m based on n if not specified
                m = args.m if args.m is not None else n * (n - 1) // 2
                max_w = args.max_w if args.max_w is not None else n
                
                # Run multiple test cases and average the times
                phase1_time_sum = 0
                phase2_time_sum = 0
                total_time_sum = 0
                valid_runs = 0
                
                for i in range(args.test_cases):
                    # Generate graph and run algorithm with timing
                    original_graph = run_generator(n, m, t, max_w)
                    if not original_graph:
                        continue
                    
                    spanner_output, timing_info = run_t_spanner_with_timing(original_graph)
                    if not spanner_output or not timing_info:
                        continue
                    
                    if all(key in timing_info for key in ['phase1', 'phase2', 'total']):
                        phase1_time_sum += timing_info['phase1']
                        phase2_time_sum += timing_info['phase2']
                        total_time_sum += timing_info['total']
                        valid_runs += 1
                        
                        if args.verbose:
                            print(f"    Run {i+1}: Phase1={timing_info['phase1']}μs, "
                                  f"Phase2={timing_info['phase2']}μs, "
                                  f"Total={timing_info['total']}μs")
                
                # Calculate averages if we have valid runs
                if valid_runs > 0:
                    avg_phase1 = phase1_time_sum / valid_runs
                    avg_phase2 = phase2_time_sum / valid_runs
                    avg_total = total_time_sum / valid_runs
                    
                    phase1_times[t].append(avg_phase1)
                    phase2_times[t].append(avg_phase2)
                    total_times[t].append(avg_total)
                    
                    print(f"    Average times for t={t}: Phase1={avg_phase1:.1f}μs, "
                          f"Phase2={avg_phase2:.1f}μs, Total={avg_total:.1f}μs")
                else:
                    print(f"    No valid timing data for n={n}, t={t}")
                    # Append None or 0 to maintain alignment with n_values
                    phase1_times[t].append(None)
                    phase2_times[t].append(None)
                    total_times[t].append(None)
        
        # Generate plots
        if any(all(x is not None for x in times) for times in phase1_times.values()):
            plot_time_comparison(n_values, phase1_times, 
                               f"T-Spanner Phase 1 Execution Time")
        
        if any(all(x is not None for x in times) for times in phase2_times.values()):
            plot_time_comparison(n_values, phase2_times, 
                               f"T-Spanner Phase 2 Execution Time")
        
        if any(all(x is not None for x in times) for times in total_times.values()):
            plot_time_comparison(n_values, total_times, 
                               f"T-Spanner Total Execution Time")
    
    else:
        if args.m is None:
            args.m = args.n * (args.n - 1) // 2
        if args.max_w is None:
            args.max_w = args.n
        if args.m > args.n * (args.n - 1) // 2:
            print(f"Warning: m exceeds maximum possible edges. Setting m to {args.n * (args.n - 1) // 2}.")
            args.m = args.n * (args.n - 1) // 2
        if args.verbose:
            print(f"Test parameters: n={args.n}, m={args.m}, t={args.t}, max_w={args.max_w}")
        
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