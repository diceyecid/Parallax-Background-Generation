# Reference: https://github.com/niranjantdesai/image-blending-graphcuts/blob/master/src/graph_cuts.py
# No other reference from this repo

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def plot_graph_2d(graph, nodes_shape, plot_weights=False,
                  plot_terminals=True, font_size=1):
    """
    Plot the graph to be used in graph cuts
    :param graph: PyMaxflow graph
    :param nodes_shape: patch shape
    :param plot_weights: if true, edge weights are shown
    :param plot_terminals: if true, the terminal nodes are shown
    :param font_size: text font size
    """
    X, Y = np.mgrid[:nodes_shape[0], :nodes_shape[1]]

    aux = np.array([Y.ravel(), X[::-1].ravel()]).T
    positions = {i: v for i, v in enumerate(aux)}
    positions['s'] = (-1, nodes_shape[0] / 2.0 - 0.5)
    positions['t'] = (nodes_shape[1], nodes_shape[0] / 2.0 - 0.5)

    nxgraph = graph.get_nx_graph()
    if not plot_terminals:
        nxgraph.remove_nodes_from(['s', 't'])

    plt.clf()
    nx.draw(nxgraph, pos=positions)
    if plot_weights:
        edge_labels = {}
        for u, v, d in nxgraph.edges(data=True):
            edge_labels[(u, v)] = d['weight']
        nx.draw_networkx_edge_labels(nxgraph,
                                     pos=positions,
                                     edge_labels=edge_labels,
                                     label_pos=0.3,
                                     font_size=font_size)
    plt.axis('equal')
    plt.show()
