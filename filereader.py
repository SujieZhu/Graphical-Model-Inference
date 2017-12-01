import sys
import os
import numpy as np

class Graph:
    """
    Definition of the class of the graph

    Attributes:
        graph_type: Markov or Bayes But the project only consider Markov
        node_number: total number of the node. Also the range of the node value form 0 to node_number-1
        variable_cordinary: a list which store the cordinary of each node where the node is the index and the corresponding value to the index is the nodes's cordinary
        clique_number: the number of the cliques provided by the file
        cliques: a list to restore each clique. Each clique is one object of the Clique class which 
        include the information of the nodes and the look_up_table for the clique
        adjacent: A set to store each node's adjacent node. To store the graph structure
        node_in_clique: A set to store each node's cliques that the node is included in
    """
    def __init__( self, graph_type, node_number, variable_cordinary, clique_number):
        self.graph_type = graph_type
        self.node_number = node_number
        self.variable_cordinary = variable_cordinary
        self.clique_number = clique_number
        self.cliques = []
        self.adjacent = {}
        self.node_in_clique = {}
        for i in range(0,node_number):
            self.adjacent[i] = []
            self.node_in_clique[i] = []
        self.evidence = {}


    def add_clique(self, index_of_clique, clique):
        self.cliques.append(clique)
        for i in range(clique.size):
            node = clique.nodes[i]
            self.node_in_clique[node].append(index_of_clique)
            for j in range(i+1, clique.size):
                adjacent_node = clique.nodes[j]
                if adjacent_node not in self.adjacent[node]:
                    self.adjacent[node].append(adjacent_node)
                    self.adjacent[adjacent_node].append(node)

    def add_clique_table(self, index_of_clique, table):
        size = ()
        for node in self.cliques[index_of_clique].nodes:
            size = size + (self.variable_cordinary[node],)
        # print(size)
        self.cliques[index_of_clique].set_table(np.array(table).reshape(size))

    def set_evidence(self, evidence):
        self.evidence = evidence





class Clique:
    """
    Definition of the class of a clique

    Attributes:
        size:  the size of the clique
        nodes: the numpy array to store the nodes in the clique
        table: the numpy ndarray to store the psi look up table
    """
    def __init__( self, size, nodes):
        self.size = size
        self.nodes = nodes 
        self.table = np.array([])

    def set_table(self, table):
        # print(self.size)
        # print(self.nodes)
        # print(table.shape)
        self.table = table



def file_reader(file_name):
    dir = os.path.dirname(os.path.realpath(__file__))
    ### read the uai file
    with open(dir + '/uai/' + file_name) as f:
        line = f.readline()
        graph_type = line.strip('\n')
        print (graph_type)
        node_number = int(f.readline())
        print (node_number)
        line = f.readline().strip(' \n').split(' ')
        variable_cordinary = list(map(int, line))
        print (variable_cordinary)
        clique_number = int(f.readline())
        print (clique_number)
        graph = Graph(graph_type, node_number, variable_cordinary, clique_number)
        
        for i in range(clique_number): # start from 0
            line = f.readline().strip('\n')
            try:
                line = np.array(list(map(int,line.split('\t'))))
            except Exception as e:
                line = np.array(list(map(int,line.split(' '))))    
            # print(line)
            size = line[0]
            # print(size)
            nodes = line[1:]
            # print(nodes)
            clique = Clique(size, nodes)
            graph.add_clique(i, clique)


        for i in range(clique_number):
            line = f.readline().strip('\n')
            if line == '':
                line = f.readline().strip('\n')
            table_size = int(line)
            # print(table_size)
            read = 0
            psi = []
            while read < table_size:
                line = f.readline().strip('\n').strip(' ').split(' ')
                read = read + len(line)
                psi.append(list(map(float,line)))
            graph.add_clique_table(i, psi)



        print(graph.adjacent[1])
        print(graph.node_in_clique[1])


    ### read the evidence file
    with open(dir + '/uai/' + file_name +'.evid') as evidence:
        line = evidence.readline().strip('\n')
        try:
            line = np.array(list(map(int,line.split('\t'))))
        except Exception as e:
            line = np.array(list(map(int,line.split(' '))))    
        evid_size = line[0]
        if evid_size != 0:
            evidence = {} 
            for i in range(0, evid_size):
                evidence[line[2*i+1]] = line[2*i+2]
            graph.set_evidence(evidence)

    print(graph.evidence)


if __name__ == '__main__':
    file_reader('2.uai')
    file_reader('3.uai')
    file_reader('4.uai')
