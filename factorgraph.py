import numpy as np
from graph import Graph
import time

class FactorGraph:

    def __init__(self, graph):
        self.nodes = []
        map_n_to_node = {}
        for k in graph.node_sharing_cliques:
            node = Node(k, graph.variable_cardinality[k])
            node.set_factors(list(graph.node_sharing_cliques[k]))
            self.nodes.append(node)    
            map_n_to_node[k] = node

        for factor in graph.cliques:
            #print("factor",factor.nodes_list)
            for n in factor.nodes_list:
                factor.two_side.append(map_n_to_node[n])

        self.factors = graph.cliques[:]

    def initial_message(self):
        for node in self.nodes:
            node.initial_message()
        for factor in self.factors:
            factor.initial_message() 
        #print("initial_message")

    def LBP(self, max_times = 400, normalize = True):
        self.initial_message()
        count = 1
        start = time.clock()
        while count < max_times:
            count = count + 1
            convergence = True
            for node in self.nodes:
                result = node.update_message(normalize)
                convergence = convergence and result
            for factor in self.factors:
                result = factor.update_message(normalize)
                convergence = convergence and result
            if convergence :
                break
            #print("Iteration", count, "\tconvergence:", convergence)
            #print('message from',self.factors[0].nodes_list[0])
            #print('to',self.factors[0].nodes_list[0])
            #print(self.factors[0].message[0])
            #print('nodes:',self.nodes[0].message)
            #print('nodes:',self.nodes[1].message)
        print("Terminate after",count,"Iteration")
        #stable message
        #for factor in self.factors:
        #    print(factor.nodes)
        #    print(factor.message)
        return count, convergence    

    def calculate_z(self):
        result = 0;
        for node in self.nodes:
            result += node.calculate_tau_s()
        #print("A()", result)
        #for node in self.nodes:
        #    print("node", node.tau)

        #sorted(self.factors, key = lambda x:x.size)
        for factor in self.factors:
            result += factor.collect_message(normalize= True)
        print("Log(Z)", result)
        return result





class Node:
    def __init__(self, name, cardinality):
        self.name = name
        self.cardinality = cardinality
        self.factors = None
        self.message = []
        self.has_single_clique = False
        self.single_clique = None
        self.tau = None
        #print('node', name, 'built')

    def set_factors(self, factor_list):
        self.factors = factor_list
        for factor in factor_list:
            if factor.size == 1:
                self.has_single_clique = True
                self.single_clique = factor
                #print(factor.table)
        #print(self.factors)

    def initial_message(self):
        for i in range(len(self.factors)):
            self.message.append(np.ones(self.cardinality))
    
    def provide_message(self, factor):
        #for factor in self.factors:
        #    print(factor.nodes)
        #print(len(self.factors), len(self.message))
        for i in range(len(self.factors)):
            if self.factors[i] == factor:
                return self.message[i]

    def update_message(self, normalize = True):
        #print("node update_message")
        old_message = self.message[:]
        
        multiply = np.ones(self.cardinality) 
        input_message = []
        for i in range(len(self.factors)):
            im = self.factors[i].provide_message(self)
            multiply *= im
            input_message.append(im)
        #print(multiply)

        convergence = True
        for i in range(len(self.factors)):
            out = multiply/input_message[i] #divide this node's input message
            out[out == np.inf] = 0.0
            out = np.nan_to_num(out)
            if normalize:
                out = out/out.sum()
            self.message[i] = out
            convergence = convergence and (sum(np.isclose(old_message[i], self.message[i]))==self.cardinality)
        #print(convergence)
        return convergence


    def calculate_tau_s(self, normalize = True):
        self.tau = np.ones(self.cardinality) 
        for i in range(len(self.factors)):
            im = self.factors[i].provide_message(self)
            #print("incoming",im)
            self.tau *= im
            #print(self.tau)
        if self.has_single_clique:
            self.tau *= self.single_clique.table
        #print("node", self.tau)
        if normalize:
            self.tau = self.tau/self.tau.sum()
        #print("node", self.tau)
        result = np.log(self.tau)
        result *= self.tau

        return -result.sum()

