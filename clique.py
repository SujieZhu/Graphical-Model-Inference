import numpy as np

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
        self.nodes = set(nodes)
        self.nodes_list = list(nodes)
        self.table = np.array([])

    def set_table(self, table):
        """Set the clique's look up table psi"""
        self.table = table

    def times(self, clique, dimension):
        self.nodes.union(clique.nodes)
        self.node_list = list(self.nodes)
        #print(self.nodes_list)
        new_dimension = tuple(map(lambda x:dimension[x] if x in clique.nodes_list else 1, self.nodes_list))
        #print('new_dimension', new_dimension)
        #print('origin_dimension', self.nodes)
        #print('small', clique.nodes)
        if self.table.size == 0:
            self_dimension = tuple(map(lambda x:dimension[x], self.nodes_list))
            self.table = np.ones(self_dimension)
        np.multiply(clique.table.reshape(new_dimension), self.table, out = self.table)
        #print('after time', self.nodes)
        #print(self.table)


    def condition(self, evidence, dimension):
        #print('*'*20)
        #print('Before condition')
        #print('vars',self.nodes)
        #print('table',self.table)
        axis = tuple( evidence[v] if v in evidence else slice(None) for v in self.nodes )
        evidence_vars = [ v for j,v in enumerate(self.nodes) if axis[j] != slice(None) ]
        #print('evidence_vars',evidence_vars)
        #print('axis', axis)
        shape = tuple(map(lambda x:dimension[x], self.nodes_list))
        self.table = self.table[axis].reshape(shape)
        #self.nodes -= set(evidence_vars)
        #self.nodes_list = list(self.nodes)
        #print('vars',self.nodes)
        #print('table',self.table)

    def sum(self, remain=None, out=None):
        if (remain is None): elim = self.nodes
        else:
            elim = self.nodes - remain
        #print('*'*30, 'eliminate', self.nodes)
        #print('to eliminate', elim)
        #print(self.table, self.table.shape)
        if len(elim)==len(self.nodes):
          self.table = np.sum(self.table)
        else:
          axis = tuple(self.nodes_list.index(x) for x in elim)
          self.table = np.sum(self.table, axis=axis)
        self.nodes = self.nodes - elim
        #print('*'*30, 'after eliminate', self.nodes)
        #print(self.table, self.table.shape)