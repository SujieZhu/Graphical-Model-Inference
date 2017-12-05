import sys
import os
import numpy as np

class Graph:
    """
    Definition of the class of the graph

    Attributes:
        graph_type: Markov or Bayes But the project only consider Markov
        node_number: total number of the node. Also the range of the node value form 0 to node_number-1
        variable_cardinality: a list which store the cardinality of each node where the node is the index and the corresponding value to the index is the nodes's cardinality
        clique_number: the number of the cliques provided by the file
        cliques: a list to restore each clique. Each clique is one object of the Clique class which 
        include the information of the nodes and the look_up_table for the clique
        adjacent: A dict to store each node's adjacent node. To store the graph structure
        node_sharing_cliques: A dict to store each node's cliques that this node is included in
        evidence: the provided evidence information stored in a dict

    New: 
        change the clique's nodes to sets
        and change adjacent dict value to sets
        node_sharing_cliques dict value to set
    """
    def __init__( self, graph_type, node_number, variable_cardinality, clique_number):
        self.graph_type = graph_type
        self.node_number = node_number
        self.variable_cardinality = variable_cardinality
        self.clique_number = clique_number
        self.cliques = []
        self.adjacent = {}
        self.node_sharing_cliques = {}
        for i in range(0,node_number):
            self.adjacent[i] = set()
            self.node_sharing_cliques[i] = set()
        self.evidence = {}


    def add_clique(self, index_of_clique, clique):
        """ add the clique to the graph and update the adjacent table from the clique info. """
        self.cliques.append(clique)
        visited = set()
        for node in clique.nodes:
            self.node_sharing_cliques[node].add(clique)
            for adjacent_node in clique.nodes:
                if adjacent_node == node or adjacent_node in visited:
                    continue
                if adjacent_node not in self.adjacent[node]:
                    self.adjacent[node].add(adjacent_node)
                    self.adjacent[adjacent_node].add(node)
            visited.add(node)

    def add_clique_table(self, index_of_clique, table):
        """add the look up table for the specified clique"""
        size = ()
        for node in self.cliques[index_of_clique].nodes:
            size = size + (self.variable_cardinality[node],)
        # print(size)
        self.cliques[index_of_clique].set_table(np.array(table).reshape(size))

    def set_evidence(self, evidence):
        """ set the evidences of the graph when doing the inference"""
        self.evidence = evidence

    def min_fill_in(self, eliminated):
        min_fill = self.node_number * self.node_number
        for v in self.adjacent: # for each not eliminated nodes
            if( v in eliminated): continue
            neighbour_set = self.adjacent[v].copy()
            neighbour_set.difference_update(eliminated) # all the not eliminated neighbors
            fill_in = 0
            #print(v, neighbour_set)
            for neigh in neighbour_set:
                for other_next in neighbour_set:
                    if(other_next == neigh): continue
                    if(other_next not in self.adjacent[neigh]):
                        fill_in += 1
            #print(fill_in)
            if fill_in < min_fill:
                min_fill = fill_in
                node = v
                if min_fill == 0:
                    break

        # eliminate the min fill in node
        neighbor = self.adjacent[node].copy()
        neighbor.difference_update(eliminated)
        neighbor.add(node)
        for pre_clique in self.cliques:
            if neighbor.intersection(pre_clique.nodes) == neighbor:
                print(node, 'not add clique')
                return node, min_fill
        clique = Clique(len(neighbor), neighbor)
        self.add_clique(self.clique_number, clique)
        self.clique_number += 1
        print(node, 'add clique', neighbor)
        return node, min_fill




    def triangulation(self):
        eliminated = set()
        for i in range(self.node_number):
            node, min_fill = self.min_fill_in(eliminated)
            print('node', node,'add', min_fill)
            eliminated.add(node)


    def super_cliques(self, clique):
        first_node_cliques = self.node_sharing_cliques[list(clique.nodes)[0]].copy()
        for node in clique.nodes:
            first_node_cliques.intersection_update(self.node_sharing_cliques[node])
        return sorted(first_node_cliques, key = lambda x:x.size)

    def maxcliques(self):
        eliminate = []
        for clique in self.cliques: # eliminate one clique at one time
            super_clique = self.super_cliques(clique)
            largest = super_clique[-1]
            if(largest != clique):
                #largest.times(clique)
                eliminate.append(clique)
        self.eliminate_clique(eliminate)
        print('maxcliques:')
        for clique in self.cliques:
            print(clique.nodes)

    def eliminate_clique(self, cliques):
        for clique in cliques:
            self.cliques.remove(clique)
            for node in clique.nodes:
                self.node_sharing_cliques[node].discard(clique)





class Clique:
    """
    Definition of the class of a clique

    Attributes:
        size:  the size of the clique
        nodes: the numpy array to store the nodes in the clique
        table: the numpy ndarray to store the psi look up table
    New:
        change the clique's nodes to sets
    """
    def __init__( self, size, nodes):
        self.size = size
        self.nodes = nodes 
        self.table = np.array([])

    def set_table(self, table):
        """Set the clique's look up table psi"""
        self.table = table



def file_reader(file_name):
    """Parse the graph structure and the look up table from the uai and evid file"""
    dir = os.path.dirname(os.path.realpath(__file__))
    ### read the uai file
    with open(dir + '/uai/' + file_name) as f:
        line = f.readline()
        graph_type = line.strip('\n')
        print (graph_type)
        node_number = int(f.readline())
        print (node_number)
        line = f.readline().strip(' \n').split(' ')
        variable_cardinality = list(map(int, line))
        print (variable_cardinality)
        clique_number = int(f.readline())
        print (clique_number)
        graph = Graph(graph_type, node_number, variable_cardinality, clique_number)
        
        for i in range(clique_number): # start from 0
            line = f.readline().strip('\n')
            try:
                line = np.array(list(map(int,line.split('\t'))))
            except Exception as e:
                line = np.array(list(map(int,line.split(' '))))    
            # print(line)
            size = line[0]
            # print(size)
            nodes = set(line[1:])
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

    ### read the evidence file
    with open(dir + '/uai/' + file_name +'.evid') as evidence:
        line = evidence.readline().strip('\n').strip(' ')
        print(line)
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



    # test for the parse
    #print(graph.adjacent[1])
    #for v in graph.node_sharing_cliques[1]:
        #print(v.table)
    #print(graph.evidence)

    graph.triangulation()
    graph.maxcliques()


if __name__ == '__main__':
    file_reader('1.uai')
    # file_reader('2.uai')
    # file_reader('3.uai')
    # file_reader('4.uai')
