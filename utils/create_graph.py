"""
This file contains function used purely for testing purposes
"""
import matplotlib.pyplot as plt
import networkx as nx
import random
def create_custom_multigraph(num_nodes: int, num_edges: int):
    """
    @brief:
        Create a custom multigraph with a specified number of nodes and edges.
        Ensure the graph is connected by first creating a spanning tree and then
        adding additional edges randomly.

    @param:
        num_nodes: The number of nodes in the graph.
        num_edges: The total number of edges in the graph. Must be at least num_nodes - 1.

    @return:
        A tuple containing the undirected MultiGraph and the directed MultiDiGraph.
    """
    if num_edges < num_nodes - 1:
        raise ValueError("Number of edges must be at least num_nodes - 1 to ensure connectivity")

    G = nx.MultiGraph()
    Dir_G = nx.MultiDiGraph()

    # Create a spanning tree to ensure connectivity
    for i in range(num_nodes - 1):
        length = random.randint(1, 10)
        G.add_edge(i, i + 1, key=0, length=length)
        Dir_G.add_edge(i, i + 1, key=0, length=length)

    # Add the remaining edges randomly
    while len(G.edges) < num_edges:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v:
            length = random.randint(1, 10)
            G.add_edge(u, v, key=0, length=length)
            Dir_G.add_edge(u, v, key=0, length=length)
    return G, Dir_G

def plot_graph(G, title, eulerian_cycle=None,color="red"):
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
        edge_colors = edge_colors = [color if (u, v) in [(edge[0], edge[1]) for edge in eulerian_cycle] or (v, u) in [(edge[0], edge[1]) for edge in eulerian_cycle] else 'blue' for u, v, _ in G.edges]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
    else:
        nx.draw_networkx_edges(G, pos)

    plt.title(title)
    plt.show(block=False)
    plt.pause(0.001)