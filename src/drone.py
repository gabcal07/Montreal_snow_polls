import networkx as nx
from networkx.algorithms import euler, matching, is_eulerian
import random
import matplotlib.pyplot as plt
import itertools
import pandas as pd
import copy

"""
- We suppose that we must clear the snow on all roads of the map
- Add a boolean tha will store wheter we should clear the snow or not from the current road
"""

def to_clear(edge) -> bool:
    """
    @param: edge (The current edge)
    @brief: This function checks if the current must has to be cleared. It only returns True,
            so all edge must be cleared, but in theory it would check the real status of the road using the GPS coordinates, using
            the drones camera.
    @return: bool: True if the edge needs to be cleared, otherwise False.
    """
    return True

def plot_graph(G:nx.Graph, eulerian_cycle:list=None, title:str="") -> None:
    """
    Plots the graph with optional highlighting of an Eulerian cycle.

    @param G: nx.Graph: The graph to be plotted.
              eulerian_cycle: list: List of edges in the Eulerian cycle to be highlighted.
              str: The title of the plot.
    """
    plt.figure()  # Create a new figure
    pos = nx.spring_layout(G)
    plt.title(title)

    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=15)

    # Draw edge labels (weights)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if eulerian_cycle:
        # Highlight the Eulerian cycle
        edge_colors = ['red' if (u, v) in eulerian_cycle or (v, u) in eulerian_cycle else 'black' for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
    else:
        nx.draw_networkx_edges(G, pos)

    plt.show(block=False)
    plt.pause(0.001)  # Pause to allow the plot to update

def create_eulerian_circuit(graph_augmented, graph_original, starting_node=None):
    """
    @brief:
        Creates an Eulerian circuit in the augmented graph.

    @param: graph_aug (nx.Graph): The augmented graph.
            original_graph (nx.Graph): The original graph.

    @return: list: List of edges representing the Eulerian circuit.
    """
    # print(graph_original.edges)
    euler_circuit = []
    # print(graph_augmented.edges)
    naive_circuit = list(nx.eulerian_circuit(graph_augmented, source=starting_node))

    # print(naive_circuit)
    for edge in naive_circuit:
        if graph_original.has_edge(edge[0], edge[1]):
            # print(edge)
            edge_att = graph_original[edge[0]][edge[1]][0]['length']
            euler_circuit.append((edge[0], edge[1], edge_att))
        else:
            # print(f"Adding the new edge: {edge}")
            aug_path = nx.shortest_path(graph_original, edge[0], edge[1], weight='length')
            aug_path_pairs = list(zip(aug_path[:-1], aug_path[1:]))
            for edge_aug in aug_path_pairs:
                edge_aug_att = graph_original[edge_aug[0]][edge_aug[1]][0]['length']
                euler_circuit.append((edge_aug[0], edge_aug[1], edge_aug_att))

    return euler_circuit

def create_complete_graph(pair_weights, flip_weights=True):
    """
    @brief:
        Creates a complete graph from pairs of nodes and their shortest paths.

    @param: pairs_shortest_paths (dict): Dictionary of node pairs and their shortest path lengths.
            flip_weights (bool): If True, flips the weights to negative for max weight matching.

    @return: nx.Graph: Complete graph with shortest path lengths as weights.
    """
    g = nx.Graph()
    for k, v in pair_weights.items():
        wt_i = -v if flip_weights else v
        g.add_edge(k[0], k[1], **{'distance': v, 'weight': wt_i})
    return g

def chinese_postman(G : nx.Graph) -> list:
    """
    @brief:
        Solves the Chinese Postman Problem for an undirected graph.

        The Chinese Postman Problem (CPP) is to find the shortest closed path or circuit that visits every edge
        of a (connected) graph. If the graph has vertices of odd degree, some edges will need to be traversed more than once.

    @param G:
        The input undirected graph, where each edge has an associated weight representing the cost to traverse that edge.

    @return:
        A list of edges representing the Eulerian circuit that solves the Chinese Postman Problem.
        The list contains tuples in the form (u, v) where u and v are the vertices of the edge.
    """

    odd_degree_nodes = [v for v, d in G.degree() if d % 2 == 1]

    # Find all possible pairs of odd-degree nodes
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))

    # Calculate the shortest path between each pair of odd-degree nodes
    odd_node_pairs_shortest_paths = {}
    for pair in odd_node_pairs:
        odd_node_pairs_shortest_paths[pair] = nx.dijkstra_path_length(G, pair[0], pair[1], weight='weight')

    # Create a complete graph with odd-degree nodes as vertices and shortest path lengths as weights
    g_odd_complete = create_complete_graph(odd_node_pairs_shortest_paths, flip_weights=True)

    # Find the maximum weight matching in the complete graph
    odd_matching_dupes = nx.algorithms.max_weight_matching(g_odd_complete, True)
    odd_matching = list(pd.unique([tuple(sorted([k, v])) for k, v in odd_matching_dupes]))

    # Augment the original graph with the matching edges
    graph_aug = nx.MultiGraph(G.copy())
    for pair in odd_matching:
        graph_aug.add_edge(pair[0], pair[1], **{'length': nx.dijkstra_path_length(G, pair[0], pair[1]), 'trail': 'augmented'})

    euler_circuit = create_eulerian_circuit(graph_aug, G)
    return euler_circuit, graph_aug

def start_drone(G : nx.graph) -> list:
    """
    Dummy function to simulate the lauching of the drone
    @param:
            G (nx.graph): The map on which our drone must scan
    @return:
            return the list of edges of the eulerian cycle and the Euelerian Graph
    """
    node_list,new_graph = chinese_postman(G)

    total_distance = sum(weight for u, v, weight in node_list)
    # print("Eulerian circuit:", node_list)
    print("Distance totale en m:", total_distance)
    return node_list, new_graph, total_distance

def create_random_connected_graph(n : int , p : int) -> nx.Graph:
    """
    @brief:
        Create a randomly connected graph using the Erdos Renyl Model
    @param:
            n (int): The amount of vertices in the Graph
            p (int): Probability of creating a edge between two vertices
    """
    G = nx.erdos_renyi_graph(n, p)
    while not nx.is_connected(G):
        G = nx.erdos_renyi_graph(n, p)
    return G