"""
File to take on the SRPR (Snow Plow Routing Problem) which is a
specific type of VRP.
"""
import networkx as nx
from drone import chinese_postman
import random
import matplotlib.pyplot as plt
import itertools
import copy

def girvan_newman(G, k,most_valuable_edge=None):
    """
    @brief:
        Perform the Girvan-Newman algorithm to split the graph into subgraphs
        by removing the most central edges until the desired number of connected
        components is reached.

    @param:
        G: The input graph.
        k: The desired number of connected components.
        most_valuable_edge: A function that takes a graph as input and returns the most central edge to be removed.
                            If not provided, the edge with the highest betweenness centrality will be used.

    @return:
        A list of tuples, each containing the connected components of the graph after each split.
    """

    # If the graph is already empty, simply return its connected
    # components.
    cc = []
    if G.number_of_edges() == 0:
        cc.append(tuple(nx.connected_components(G)))
        return cc

    # If no function is provided for computing the most valuable edge,
    # use the edge betweenness centrality.
    if most_valuable_edge is None:

        def most_valuable_edge(G):
            """
            Returns the edge with the highest betweenness centrality
            in the graph `G`.
            """

            # We have guaranteed that the graph is non-empty, so this
            # dictionary will never be empty.
            betweenness = nx.edge_betweenness_centrality(G)
            return max(betweenness, key=betweenness.get)

    # The copy of G here must include the edge weight data.
    g = G.copy().to_undirected()
    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    g.remove_edges_from(nx.selfloop_edges(g))
    while g.number_of_edges() > 0 and k > 1:
        k-=1
        cc.append(_without_most_central_edges(g, most_valuable_edge))
    return cc

def _without_most_central_edges(G, most_valuable_edge):
    """
    @brief:
        Remove the most central edges from the graph until the number of connected
        components increases. The most central edge is determined by a provided function.

    @param:
        G: The input graph.
        most_valuable_edge: A function that takes a graph as input and returns the most central edge to be removed.

    @return:
        A tuple containing the new connected components of the graph after removal of the most central edges.
    """
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        edge = most_valuable_edge(G)
        G.remove_edge(*edge)
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components

def to_path_edges(G):
    """
    @brief:
        Convert the input graph to a path graph and return its edges.

    @param:
        G: The input graph.

    @return:
        A list of edges representing the path graph.
    """
    return nx.path_graph(G).edges

def get_edges_from_nodes(G: nx.Graph, nodes: list) -> list:
    """
    @brief:
        Extract edges from a given graph that connect a specified list of nodes.
        For each node in the list, find its neighbors that are also in the list
        and collect the edges connecting them.

    @param:
        G: The input graph from which edges are to be extracted.
        nodes: A list of nodes for which the edges are to be identified.

    @return:
        A list of edges where each edge is represented as a tuple (u, v, key, data).
    """
    edges = []
    for node in nodes:
        for neighbor in G.neighbors(node):
            if neighbor in nodes:
                edge_data = G.get_edge_data(node, neighbor)
                if edge_data:
                    for key, data in edge_data.items():
                        edges.append((node, neighbor,key, data))
    return edges

def zaky_euler(G: nx.MultiDiGraph, sub_graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    @brief:
        For each subgraph, start at the node with the highest degree,
        from this node try to find the shortest path to all nodes in the same subgraphs
        if it doesnt exist use the shortest path from the whole graph
    @param:
        G: The original graph of the map
        sub_graph: One of the map sub graph
    @return:
        It returns a fully connected subgraph
    """
    if len(sub_graph.degree) == 0:
        return sub_graph

    highest_node = sorted(sub_graph.degree, key=lambda x: x[1], reverse=True)[0][0]
    nodes_to_check = list(sub_graph.nodes)

    for i in nodes_to_check:
        if not nx.has_path(sub_graph, highest_node, i):
            shortest_path = nx.shortest_path(G, highest_node, i, weight="length") or nx.shortest_path(G, i, highest_node, weight="length")

            edges = to_path_edges(shortest_path)

            for u, v in edges:
                edge_data = G.get_edge_data(u, v)
                if edge_data:
                    for key in edge_data:
                        data = edge_data[key]
                        sub_graph.add_edge(u, v, key=key, **data)

    return sub_graph

def subgraph(G, cc_list):
    """
    @brief:
        Create a subgraph from the original graph by extracting edges
        that start from nodes in the given connected component list.

    @param:
        G: The original graph of the map.
        cc_list: A list of nodes representing a connected component.

    @return:
        A list of edges representing the subgraph.
    """
    sub_graph = []
    for i in cc_list:
        for edge in G.edges:
            if edge[0] == i:
                sub_graph.append(edge)
    return sub_graph

def create_multidigraph_from_edge_list(main_graph: nx.MultiDiGraph, edge_list: list) -> nx.MultiDiGraph:
    """
    @brief:
        Create a new MultiDiGraph from a list of edges, preserving edge attributes.
        The edges can include optional keys to identify specific edges in a multigraph.

    @param:
        main_graph: The original MultiDiGraph containing the full set of edges and nodes.
        edge_list: A list of edges to include in the new graph. Each edge can be a tuple
                   (u, v) or (u, v, key).

    @return:
        A new MultiDiGraph containing the specified edges with their attributes from the main graph.
    """
    new_graph = nx.MultiDiGraph()
    for edge in edge_list:
        if len(edge) == 3:
            u, v, key = edge
            if main_graph.has_edge(u, v, key=key):
                edge_data = main_graph.get_edge_data(u, v, key=key)
                new_graph.add_edge(u, v, key=key, **edge_data)
        else:
            u, v = edge
            if main_graph.has_edge(u, v):
                keys = main_graph[u][v].keys()
                for key in keys:
                    edge_data = main_graph.get_edge_data(u, v, key=key)
                    new_graph.add_edge(u, v, key=key, **edge_data)
    return new_graph

def split_graph(G: nx.Graph, Directed_G, n: int):
    """
    @brief:
        Split a graph into subgraphs using the Girvan-Newman algorithm. The resulting subgraphs
        are further processed to ensure they are Eulerian.

    @param:
        G: The original undirected graph.
        Directed_G: The directed version of the original graph.
        n: The number of splits to perform using the Girvan-Newman algorithm.

    @return:
        A list of fully connected subgraphs that are Eulerian.
    """
    split_steps = girvan_newman(Directed_G.copy(),n)
    last_step = split_steps[-1]
    sub_graphs = []

    for cc in last_step:
        cc_list = list(cc)
        sub_graph = subgraph(G,cc_list)
        G_s = create_multidigraph_from_edge_list(G, sub_graph)
        G_s = zaky_euler(G,G_s)
        sub_graphs.append(G_s)
    return sub_graphs

def build_dipath(G,eulerian_path):
    """
    @brief:
        Build a directed path from an Eulerian path by traversing the graph.
        If an edge is missing, find the shortest path using the original graph.

    @param:
        G: The original graph.
        eulerian_path: A list of edges representing the Eulerian path. Each edge is a tuple (src, dst, key).

    @return:
        A list of nodes representing the directed path.
    """
    G_p = copy.copy(G)
    path = []
    visited = []

    for (src,dst, key) in eulerian_path:

        path.append(src)

        if((src,dst,key) not in G_p.edges):
            if((dst,src,key) in G_p.edges and (dst,src) not in visited):

                curr_path = nx.shortest_path(G_p,src,dst)
                path += curr_path[1:]
                add_path(visited,curr_path)
                path.append(src)
                visited.append((dst,src))

            curr_path = nx.shortest_path(G_p, src,dst)
            add_path(visited,curr_path)
            path += curr_path[1:-1]

        visited.append((src,dst))
    return path

def add_path(visited, path):
    """
    @brief:
        Add the edges of a path to the visited list.

    @param:
        visited: A list to store visited edges.
        path: A list of nodes representing the path.

    @return:
        None. The visited list is updated in place.
    """
    for i in range(len(path)-1):
        src = path[i]
        dst = path[i+1]
        if((src,dst) not in visited):
            visited.append((src,dst))
def launch_snow_plows(G,Dir_G,n):
    """
    @brief:
        Split the graph into subgraphs, find Eulerian paths for each subgraph, and
        build directed paths to represent the routes of snow plows.

    @param:
        G: The original undirected graph.
        Dir_G: The directed version of the original graph.
        n: The number of splits to perform using the Girvan-Newman algorithm.

    @return:
        A list of edges representing the Eulerian paths for snow plows in each subgraph.
    """

    G_lst = split_graph(G,Dir_G,n)
    euler_paths = []
    for graph in G_lst:
        if graph is not None:
            g = graph.to_undirected()
            eulerian_cycle = chinese_postman(g)
            path = build_dipath(eulerian_cycle[1],eulerian_cycle[0])
            edges = get_edges_from_nodes(graph,path)
            euler_paths.append(edges)
    return euler_paths