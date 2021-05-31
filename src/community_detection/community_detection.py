from copy import deepcopy
import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx

import pandas as pd
import numpy as np
import pickle


class community_detection:
    def __init__(self):
        print('Object for COMMUNITY DETECTION')
        
    def fit(self, co_matrix_path):
        self.co_matrix = pd.read_csv(co_matrix_path)

        nodes = [id_ for id_ in self.co_matrix['start_station_id']]
        edges = [[from_, to_, self.get_edge(from_, to_)] for from_ in nodes for to_ in nodes]
        node_and_edge = {'nodes' : nodes, 'edges' : edges}


        df = pd.DataFrame(node_and_edge['edges'], columns =['from', 'to', 'value'], dtype=int)

        df_edges = deepcopy(df)
        df_edges = df_edges.rename(columns = {'from' : 'source', 'to' : 'target'})


        edges = df_edges[['source','target']].values.tolist()
        weights = [float(l) for l in df_edges.value.values.tolist()]

        G = nx.Graph(directed=True)
        G.add_edges_from(edges)
    
        for cnt, a in enumerate(G.edges(data=True)):
            G.edges[(a[0], a[1])]['weight'] = weights[cnt]

        self.nodes = nodes
    
        return G, df_edges

    def make_plot(self, G, path):
        # compute the best partition
        self.partition = community_louvain.best_partition(G)

        fig = plt.figure(figsize=(20,10))

        # draw the graph
        pos = nx.spring_layout(G)
        # color the nodes according to their partition
        cmap = cm.get_cmap('viridis', max(self.partition.values()) + 1)
        nx.draw_networkx_nodes(G, pos, self.partition.keys(), node_size=40,
                            cmap=cmap, node_color=list(self.partition.values()))
        nx.draw_networkx_edges(G, pos, alpha=0.5)
        plt.savefig(path[:-3]+'png')
        plt.show()



    def node_per_class(self):
        node_per_class = {i : [] for i in range(8)}
        for i in self.nodes:
            for cls in range(8):
                if self.partition[int(i)] == cls:
                    node_per_class[cls].append(i)
        print(node_per_class)
        return node_per_class
  

    def get_edge(self, from_, to_):
    
        row_boolean = self.co_matrix['start_station_id'] == from_
        value = self.co_matrix[row_boolean][str(float(to_))].values[0]
        
        return value