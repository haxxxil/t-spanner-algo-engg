import argparse
import random

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a random graph.")
    parser.add_argument("n", type=int, nargs="?", default=10, help="Number of nodes in the graph (default: 10)")
    parser.add_argument("m", type=int, nargs="?", help="Number of edges in the graph (default: n^2/2)")
    parser.add_argument("t", type=int, nargs="?", default=3, help="Parameter t (default: 3)")
    parser.add_argument("max_w", type=int, nargs="?", default=None, help="Maximum weight of edges (default: n)")

    # Parse arguments
    args = parser.parse_args()
    n = args.n
    m = args.m if args.m is not None else n**2 // 2
    t = args.t
    max_w = args.max_w if args.max_w is not None else n

    # Ensure m is not greater than the maximum possible number of edges in a simple graph
    max_possible_edges = n * (n - 1) // 2
    m = min(m, max_possible_edges)

    # Generate edges
    edges = set()
    while len(edges) < m:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            edge = tuple(sorted((u, v)))
            edges.add(edge)

    # Assign random weights to edges and shuffle their order
    edges = [(u, v) if random.choice([True, False]) else (v, u) for u, v in edges]
    random.shuffle(edges)
    edges_with_weights = [(u, v, random.randint(1, max_w)) for u, v in edges]

    # Print the graph
    print(n, m, t)
    for u, v, w in edges_with_weights:
        print(u, v, w)

if __name__ == "__main__":
    main()