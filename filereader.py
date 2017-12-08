import sys
import os
import numpy as np

from graph import Graph
from clique import Clique
from junction_tree import junction_tree


def file_reader(file_name):
    """Parse the graph structure and the look up table from the uai and evid file"""
    dir = os.path.dirname(os.path.realpath(__file__))
    ### read the uai file
    with open(dir + '/uai/' + file_name) as f:
        line = f.readline()
        graph_type = line.strip('\n')
        #print (graph_type)
        node_number = int(f.readline())
        #print (node_number)
        line = f.readline().strip(' \n').split(' ')
        variable_cardinality = list(map(int, line))
        #print (variable_cardinality)
        clique_number = int(f.readline())
        #print (clique_number)
        graph = Graph(graph_type, node_number, variable_cardinality, clique_number)
        
        for i in range(clique_number): # start from 0
            line = f.readline().strip('\n').strip(' ')
            #print(line)
            try:
                line = np.array(list(map(int,line.split('\t'))))
            except Exception as e:
                line = np.array(list(map(int,line.split(' '))))    
            # print(line)
            size = line[0]
            # print(size)
            nodes = list(line[1:])
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

    # graph.triangulation()
    # graph.maxcliques()
    print('test result')
    #graph.test()
    JT = graph.generate_JT()
    JT.traverse()

if __name__ == '__main__':
    file_reader('3.uai')
    # file_reader('2.uai')
    # file_reader('3.uai')
    # file_reader('4.uai')
