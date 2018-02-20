import numpy as np
from junction_tree import junction_tree
from clique import Clique


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
        for node in self.cliques[index_of_clique].nodes_list:
            size = size + (self.variable_cardinality[node],)
        # print(size)
        
        previous = self.cliques[index_of_clique].nodes_list[:]
        self.cliques[index_of_clique].nodes_list = sorted(self.cliques[index_of_clique].nodes_list)
        #print(self.cliques[index_of_clique].nodes_list)
        index = []
        for i in range(len(previous)):
            index.append(self.cliques[index_of_clique].nodes_list.index(previous[i]))
        #print("index",index)
        #print(np.array(table).reshape(size))
        self.cliques[index_of_clique].set_table(np.array(table).reshape(size).transpose(index))
        #print(self.cliques[index_of_clique].table)

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
            if neighbor.intersection(pre_clique.nodes) == neighbor: #neighbor and itself are already provided
                #print(node, 'not add clique')
                return node, min_fill
        clique = Clique(len(neighbor), neighbor)
        self.add_clique(self.clique_number, clique)
        self.clique_number += 1
        #print(node, 'add clique', neighbor)
        return node, min_fill


    def triangulation(self):
        eliminated = set()
        for i in range(self.node_number):
            node, min_fill = self.min_fill_in(eliminated)
            #print('node', node,'add', min_fill)
            eliminated.add(node)




    def super_cliques(self, clique):
        first_node_cliques = self.node_sharing_cliques[list(clique.nodes)[0]].copy()
        for node in clique.nodes:
            first_node_cliques.intersection_update(self.node_sharing_cliques[node])
        return sorted(first_node_cliques, key = lambda x:x.size)

    def maxcliques(self):
        eliminate = []
        absorb = {}
        for clique in self.cliques: # eliminate one clique at one time
            super_clique = self.super_cliques(clique)
            largest = super_clique[-1]
            if(largest != clique):
                largest.times(clique, self.variable_cardinality)
                #for supers in super_clique:
                #    if supers not in absorb:
                #        absorb[supers] = []
                #    absorb[supers].append(clique)
                eliminate.append(clique)
        
        #print('maxcliques:')
        #for clique in self.cliques:
        #    if clique in eliminate:
        #        continue
        #    if clique not in absorb:
        #        continue
        #    print('maxcliques', clique.nodes)
        #    for small_clique in absorb[clique]:
        #        print('smaller cliques', small_clique.nodes)
        #        clique.times(small_clique, self.variable_cardinality)
        #        print('after absorb', clique.table)
            #print(clique.nodes)
            #print(clique.table)
            #print(clique.table.shape)
        self.eliminate_clique(eliminate)

    def eliminate_clique(self, cliques):
        for clique in cliques:
            self.cliques.remove(clique)
            for node in clique.nodes:
                self.node_sharing_cliques[node].discard(clique)

    def condition(self):
        for evidence in self.evidence:
            self.variable_cardinality[evidence] = 1
        for clique in self.cliques:
            clique.condition(self.evidence, self.variable_cardinality)

    def generate_JT(self):
        self.condition()
        self.triangulation()
        self.maxcliques()

        JT = junction_tree(self.cliques, self.variable_cardinality)
        return JT

    def test(self):
        all_clique = Clique(self.node_number, range(self.node_number))
        for clique in self.cliques:
            all_clique.times(clique, self.variable_cardinality)
        #print(all_clique.table)
        all_clique.sum()
        print('ground truth?')
        print(all_clique.table)

    def pairwise(self):
        eliminate = []
        for clique in self.cliques:
            if(clique.size > 2):
                self.add_pairwise(clique)
                eliminate.append(clique)
                #print("eliminate", clique.nodes)
        self.eliminate_clique(eliminate)

    def add_pairwise(self,clique):
        new_card = clique.table.size
        self.variable_cardinality.append(new_card)
        #print("Z size", new_card)
        label = self.node_number
        
        Z = Clique(1,[label])
        self.adjacent[self.node_number] = set()
        self.node_sharing_cliques[self.node_number] = set()
        self.node_number += 1
        self.add_clique(self.clique_number, Z)

        table = clique.table.reshape(1,new_card)
        #print("table:",table[0,2])
        #print("origin",clique.table[0,1,0])
        #print(table)
        self.clique_number += 1
        self.add_clique_table(self.clique_number -1, table)
        #print("Z", Z.nodes_list, Z.table)

        time = new_card
        for node in clique.nodes_list:
            labels = [node,label]
            Z_x= Clique(2,labels)
            #print(Z_x.nodes_list)
            self.add_clique(self.clique_number, Z_x)
            self.clique_number += 1
            cardinality = self.variable_cardinality[node]
            table = np.zeros((cardinality,new_card))
            time = time/cardinality
            y = 0
            count = 0
            for i in range(new_card):
                table[y,i] =1
                count += 1
                if count == time:
                    count = 0;
                    y = (y+1)%cardinality
            #print(table[2])
            self.add_clique_table(self.clique_number -1, table)
            #print("Z xi table", Z_x.nodes_list, Z_x.table.shape)
