import numpy as np


class junction_tree:
    def __init__(self, maxcliques, variable_cardinality):
        self.JT_nodes = maxcliques # lists
        self.next = {} # maxclique graph
        self.child = {} # generated maxclique's junction tree
        self.parent = []
        self.variable_cardinality = variable_cardinality

    def build_tree(self):
        edges = self.build_graph()
        self.MaximumSpanningTree(edges)
        root = self.JT_nodes[0]
        added = set()
        next_round = [root]
        while len(next_round) != 0:
            new_next_round = []
            for clique in next_round:
                added.add(clique)
                if clique not in self.next:
                    continue
                for adjacent_clique in self.next[clique]:
                    if adjacent_clique in added:
                        continue
                    if clique not in self.child:
                        self.child[clique] = set()
                    self.child[clique].add(adjacent_clique)
                    new_next_round.append(adjacent_clique)
                    # added.add(adjacent_clique)
            next_round = new_next_round[:]
            del new_next_round
                
        return root

    def build_graph(self):
        edges = []
        for i in range(len(self.JT_nodes)):
            self.parent.append(i)
            for j in range(i+1, len(self.JT_nodes)):
                if len(self.JT_nodes[i].nodes.intersection(self.JT_nodes[j].nodes)) != 0:
                    edges.append((i,j))
        return edges

    def MaximumSpanningTree(self, edges):
        #print('*'*30)
        #for clique in self.JT_nodes:
        #    print('JT node', clique.nodes)
        # print('before sort')
        # for edge in edges:
        #    print('edge', edge)
        
        edges = sorted(edges, key = lambda x:len(self.JT_nodes[x[0]].nodes.intersection(self.JT_nodes[x[1]].nodes)),reverse = True)
        
        #print('After sort')
        #for edge in edges:
        #   print('edge', edge)

        for edge in edges:
            parent_i = self.find_parent(edge[0])
            parent_j = self.find_parent(edge[1])
            if parent_i != parent_j:
                self.parent[parent_i] = parent_j 
                if self.JT_nodes[edge[0]] not in self.next:
                    self.next[self.JT_nodes[edge[0]]] = set()
                if self.JT_nodes[edge[1]] not in self.next:
                    self.next[self.JT_nodes[edge[1]]] = set()
                self.next[self.JT_nodes[edge[0]]].add(self.JT_nodes[edge[1]])
                self.next[self.JT_nodes[edge[1]]].add(self.JT_nodes[edge[0]]) 
                #print(self.JT_nodes[edge[0]].nodes, 'adding edes',self.JT_nodes[edge[1]].nodes )    



    def find_parent(self, x):
        if self.parent[x] == x:
            return x
        else:
            self.parent[x] = self.find_parent(self.parent[x])
            return self.parent[x]



    def traverse(self):
        root = self.build_tree()
        #print('*'*30)
        #print('traverse')
        #for x in self.child:
        #    print(x.nodes)
        #    for v in self.child[x]:
        #        print('next', v.nodes)
        #print('*'*30)
        #print('PostOrder')
        self.PostOrder(root, root)
        root.sum()
        print('Log(Z)',np.log(root.table))

    def PostOrder(self, root, father):
        if root in self.child:
            for child in self.child[root]:
                self.PostOrder(child,root)
                root.times(child, self.variable_cardinality)
        #print(root.nodes, '\t parent:', father.nodes)
        root.sum(root.nodes.intersection(father.nodes))
        return
