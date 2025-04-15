import sys
import os
import random
import time
import networkx as nx
from colorama import init, Fore, Style
import matplotlib.pyplot as plt

# Initialize colorama
init(autoreset=True)

# Add the src directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from drone import start_drone

def create_random_custom_graph(num_nodes: int, num_edges: int) -> nx.MultiGraph:
    """
    Create a custom graph with randomly generated edges and specific attributes, ensuring the graph is connected.

    @param
        num_nodes: Number of nodes in the graph.
        num_edges: Number of edges to create.

    @return: A NetworkX MultiGraph with the specified number of nodes and randomly generated edges.
    """
    if num_edges < num_nodes - 1:
        raise ValueError("Number of edges must be at least num_nodes - 1 to ensure connectivity")

    G = nx.MultiGraph()

    # Create a spanning tree to ensure connectivity
    for i in range(num_nodes - 1):
        length = random.randint(1, 10)
        G.add_edge(i, i + 1, key=0, length=length)

    # Add the remaining edges randomly
    while len(G.edges) < num_edges:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v:
            length = random.randint(1, 10)
            G.add_edge(u, v, key= 0, length=length)

    return G

def plot_graph(G, title, eulerian_cycle=None):
    """
    Plots the graph with optional highlighting of an Eulerian cycle.

    @param G: nx.Graph: The graph to be plotted.
    @param title: str: The title of the plot.
    @param eulerian_cycle: list: List of edges in the Eulerian cycle to be highlighted.
    """
    plt.figure()  # Create a new figure
    pos = nx.spring_layout(G)

    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=15)

    # Draw edge labels (weights)
    edge_labels = nx.get_edge_attributes(G, 'length')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if eulerian_cycle:
        # Highlight the Eulerian cycle
        edge_colors = ['red' if (u, v) in eulerian_cycle or (v, u) in eulerian_cycle else 'black' for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
    else:
        nx.draw_networkx_edges(G, pos)

    plt.title(title)
    plt.show(block=False)
    plt.pause(0.001)  # Pause to allow the plot to update

def test_custom_graph(num_tests: int, num_nodes: int, num_edges: int):
    """
    Test the start_drone method on randomly generated custom graphs.

    @param num_tests: Number of tests to run.
    @param num_nodes: Number of nodes in each graph.
    @param num_edges: Number of edges in each graph.
    @return: Number of passed tests.
    """
    passed_tests = 0

    for i in range(num_tests):
        G = create_random_custom_graph(num_nodes, num_edges)

        print(f"{Fore.CYAN}{Style.BRIGHT}Testing Custom Graph {i + 1}")
        special_edges, new_G = start_drone(G)
        is_eulerian = nx.is_eulerian(new_G)
        if is_eulerian:
            passed_tests += 1
            print(f"{Fore.GREEN}Graph is Eulerian: {is_eulerian}")
        else:
            print(f"{Fore.RED}Graph is Eulerian: {is_eulerian}")
        if i == num_tests - 1:
            # Uncomment the lines below to plot the graphs if desired
            plot_graph(G, title=f"Custom Graph {i + 1}")
            plot_graph(new_G, title=f"Eulerian Graph {i + 1}", eulerian_cycle=special_edges)

    return passed_tests

if __name__ == "__main__":
    total_tests = 30
    num_tests_per_size = 10

    start_time = time.time()

    print(f"{Fore.YELLOW}{Style.BRIGHT}Starting tests on small sized graphs...")
    passed_tests_small = test_custom_graph(num_tests_per_size, 15, 20)

    print(f"{Fore.YELLOW}{Style.BRIGHT}Starting tests on medium sized graphs...")
    passed_tests_medium = test_custom_graph(num_tests_per_size, 200, 205)

    print(f"{Fore.YELLOW}{Style.BRIGHT}Starting tests on large sized graphs...")
    passed_tests_large = test_custom_graph(num_tests_per_size, 500, 505)

    passed_tests = passed_tests_small + passed_tests_medium + passed_tests_large
    end_time = time.time()

    duration = end_time - start_time

    print(f"{Fore.YELLOW}{Style.BRIGHT}Tests completed. You passed {passed_tests} tests out of {total_tests} in {duration:.2f} seconds.")
    input("Press enter to continue ... ")
