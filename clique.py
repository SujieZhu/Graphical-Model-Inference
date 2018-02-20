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

        self.message = []
        self.two_side = []
        self.tau = None;

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
        #print(len(self.table.shape))


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
        

    def initial_message(self):
        for node in self.two_side:
            self.message.append(np.ones(node.cardinality))

    def provide_message(self, node):
        for i in range(self.size):
            if self.two_side[i] == node:
                return self.message[i]

    def update_message(self, normalize=True):
        #print("factor update_message")
        old_message = self.message[:]
        table = self.table.copy()
        #print("nodes",self.nodes_list)
        #print("shape",self.table.shape)

        # compared with the node point, factor need to matrix multiply the input messages
        # from the node
        # then divide the output direction's input message  
        input_message = []
        for i in range(len(self.two_side)):
            im = self.two_side[i].provide_message(self)
            axis = np.ones(len(table.shape),int)
            axis[i] = -1
            im = im.reshape(axis)
            input_message.append(im)
            #print("im", im.shape)
            #print("table", table.shape)
            table *= im
        #print('table' ,table)

        convergence = True
        indexs = range(len(table.shape))
        for i in range(len(self.two_side)):
            out = table/input_message[i] #divide this node's input message
            out[out == np.inf] = 0.0
            out = np.nan_to_num(out)
            axis = tuple(list(indexs[:i])+list(indexs[i+1:]))
            out_message = out.sum(axis=axis)
            if normalize:
                out_message = out_message/out_message.sum()
            self.message[i] = out_message
            similarity = sum(np.isclose(old_message[i], self.message[i]))==self.two_side[i].cardinality
            convergence = convergence and similarity
        #print(convergence)
        return convergence

    def collect_message(self, normalize = True):
        epsilon = 0.0000005
        table = self.table.copy()
        table_2 = self.table.copy()
        for i in range(len(self.two_side)):
            im = self.two_side[i].provide_message(self)
            axis = np.ones(len(table.shape),int)
            axis[i] = -1
            im = im.reshape(axis)
            table *= im

        if normalize:
            table = table/table.sum()
        
        self.tau = table[:]
        #print("Tau",self.tau)
        #print("table",table)
        table_2[table_2 == 0] = epsilon
        tmp = table * np.log(table_2)
        #print(self.tau)
        result = tmp.sum()

        ##calculate I_st
        if self.size > 1:
            for i in range(len(self.two_side)):
                tau = self.two_side[i].tau[:]
                axis = np.ones(len(table.shape),int)
                axis[i] = -1
                tau = tau.reshape(axis)
                table = table/tau
                table[table == 0] = epsilon
                #table = np.nan_to_num(table)
            #print(table)
            #print(self.tau)
            #print(np.log(table))
            table = self.tau*np.log(table)
            result -= table.sum()
        #print("consistence",self.tau)
        return result


