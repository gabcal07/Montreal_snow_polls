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

def create_handmade_graph(edges):
    """
    Create a MultiGraph from a list of edges with specific lengths.

    @param edges: List of edges in the form (src, dest, length).
    @return: A NetworkX MultiGraph with the specified edges.
    """
    G = nx.MultiGraph()
    for u, v, length in edges:
        G.add_edge(u, v, length=length)
    return G

def plot_graph(G, title, eulerian_cycle=None):
    """
    Plots the graph with optional highlighting of an Eulerian cycle.

    @param G: nx.Graph: The graph to be plotted.
            title: str: The title of the plot.
            eulerian_cycle: list: List of edges in the Eulerian cycle to be highlighted.
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

def calculate_total_cost(edges):
    """
    Calculate the total cost of the edges in the Eulerian cycle.

    @param edges: List of edges in the Eulerian cycle.
    @return: Total cost of the Eulerian cycle.
    """
    return sum(weight for _, _, weight in edges)

def test_handmade_graph(edges, expected_minimum_cost):
    """
    Test the start_drone method on a handmade graph.

    @param edges: List of edges in the form (src, dest, length).
                expected_minimum_cost: The expected minimum cost of the Eulerian circuit.
    """
    G = create_handmade_graph(edges)

    print(f"{Fore.CYAN}{Style.BRIGHT}Testing Handmade Graph")
    special_edges, new_G = start_drone(G)
    is_eulerian = nx.is_eulerian(new_G)
    total_cost = calculate_total_cost(special_edges)

    if is_eulerian and total_cost == expected_minimum_cost:
        print(f"{Fore.GREEN}Graph is Eulerian: {is_eulerian}, Total cost: {total_cost}, Expected minimum cost: {expected_minimum_cost}")
    else:
        print(f"{Fore.RED}Graph is Eulerian: {is_eulerian}, Total cost: {total_cost}, Expected minimum cost: {expected_minimum_cost}")

    # plot_graph(G, title="Handmade Graph")
    plot_graph(new_G, title="Eulerian Graph", eulerian_cycle=special_edges)

if __name__ == "__main__":
    print(f"{Fore.YELLOW}{Style.BRIGHT}Starting tests on handmade graphs...")

    # Test Graph 1: Simple Triangle
    edges_1 = [(0, 1, 1), (1, 2, 2), (2, 0, 3)]
    test_handmade_graph(edges_1, expected_minimum_cost=6)

    # Test Graph 2: Square with Diagonal
    edges_2 = [(0, 1, 1), (1, 2, 2), (2, 3, 1), (3, 0, 2), (0, 2, 1)]
    test_handmade_graph(edges_2, expected_minimum_cost=8)

    # Test Graph 3: More Complex Graph
    edges_3 = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 0, 5), (0, 2, 1)]
    test_handmade_graph(edges_3, expected_minimum_cost=16)

    print(f"{Fore.YELLOW}{Style.BRIGHT}Tests completed.")
    input("Press Enter to exit...")