from random import choice, seed
import logging
from graph import Graph, decompose_into_connected_components
from sys import argv

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

NONE = 0
UNCONNECTED = 1

num_bags = 0
class TreeDecomposition:

    def __init__(self, bag_content, tree_id, children):
        self.bag_content = bag_content
        self.tree_id = tree_id
        self.children = children

        global num_bags
        num_bags += 1
        self.id = num_bags

    def check_subtree(self, vertex):
        pass

    def extract_subtree(self, vertex):
        subtrees = []
        for child in self.children:
            subtree = child.extract_subtree()
            if subtree not in [NONE, UNCONNECTED]:
                subtrees.append(subtree)

        if vertex not in self.bag_content:
            if len(subtrees) == 0:
                logging.error(f'Vertex {vertex} has no bag in the subtree under {self.id}')
                return NONE
            if len(subtrees) >= 2:
                logging.error(f'Vertex {vertex} has two unconnected bags in the two disjoint subtrees {[subtree.id for subtree in subtrees]}')
                return UNCONNECTED
            return subtrees[0]
        else:
            subtree = TreeDecomposition(self.bag_content, self.tree_id, subtrees)
            return subtree

    def validate(self, graph):
        subtrees = dict()
        for vertex in graph.adjacent:
            # compute connected components of all the bags containing 'vertex'
            components = self.extract_subtree(vertex)

            # there should be exactly one such component
            if len(components) == 0:
                logging.error(f'Vertex {vertex} has no bags')
                return False
            if len(components) > 1:
                logging.error(f'Vertex {vertex} has two unconnected bags')
                return False

            subtrees[vertex] = components[0]

        # check that all edges are bagged
        for vertex, neighbours in graph.adjacent.items():
            subtree = subtrees[vertex]

            for neigh in neighbours:
                neigh_subtree = subtrees[neigh]
                share_bag = False
                for bag in subtree:
                    if bag in neigh_subtree:
                        share_bag = True
                        logging.debug(f'The edge between vertices {vertex} and {neigh} is covered by the bag {bag}')
                        break
                if not share_bag:
                    logging.error(f'The edge between vertices {vertex} and {neigh} is not covered')
                    return False
        return True

    def __str__(self):
        s = ''
        for child in self.children:
            s += str(child)
        s += f'Bag {self.tree_id}, indexed {self.id}, contains the vertices {self.bag_content}\n'
        return s

UNKNOWN = 0
FAILED = 1
SUCCESS = 2

num_nodes = 0
root_graph = None

class DecompositionNode:

    def __init__(self, pred, labelled_subgraph, is_bag):
        self.predecessor = pred
        self.subgraph = labelled_subgraph
        self.successors = []
        self.is_bag = is_bag
        self.strategy = None
        self.status = UNKNOWN

        global num_nodes
        num_nodes += 1
        self.id = num_nodes

    def delete(self):
        for succ in self.successors:
            succ.delete()

        pred = self.predecessor
        pred.successors.remove(self)
        if self is pred.strategy:
            pred.strategy = None
        self.predecessor = None

        del self

    def add_child(self, child):
        self.successors.append(child)

    def set_status(self, new_status):
        self.status = new_status

    def decompose_subgraph(self):
        assert self.is_bag
        components = decompose_into_connected_components(self.subgraph)
        for comp in components:
            child = DecompositionNode(pred=self, labelled_subgraph=comp, is_bag=False)
            self.add_child(child)

    def extract_tree_decomposition(self):
        children = []
        for succ in self.successors:
            child_decomposition = succ.extract_tree_decomposition()
            children.append(child_decomposition)
        tree_decomposition = TreeDecomposition(self.subgraph.cops, self.id, children)
        return tree_decomposition

    def dot_subgraphs(self):
        s = ''
        for child in self.successors:
            s += child.dot_subgraphs()

        edge_color = '#00ced172'
        bag_color = '#ff8c00b2'
        status_color = {
            UNKNOWN: 'gray',
            FAILED: 'crimson',
            SUCCESS: 'green3'
        }

        color = bag_color if self.is_bag else edge_color
        node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
        node_label = f'Bag {self.id}' if self.is_bag else f'Edge {self.id}'

        s += f'subgraph cluster_{node_name} '
        s += '{\n'
        s += f'graph [label="{node_label}", style=rounded, '
        s += f'bgcolor="{color}", penwidth=8, color={status_color[self.status]}]\n'
        s += 'edge [penwidth=1, dir=none]\n'
        s += f'{node_name} [style=invis]\n'
        subgraph_string = self.subgraph.dot_string(node_name, root_graph)
        s += subgraph_string
        s += '}\n'

        if self.predecessor is not None:
            strategy_color = 'red'
            node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
            pred_name = f'b{self.predecessor.id}' if self.predecessor.is_bag else f'e{self.predecessor.id}'
            color = f', color={strategy_color}' if self == self.predecessor.strategy else ''
            s += f'{pred_name} -> {node_name} [ltail=cluster_{pred_name}, '
            s += f'lhead=cluster_{node_name}{color}]\n'

        return s

    def dot_string(self):
        s = 'digraph {\n'
        s += 'graph [compound=true, ranksep=1, nodesep=1]\n'
        s += 'edge [penwidth=3]\n'
        s += 'node [style=filled, color=aliceblue]\n'

        s += self.dot_subgraphs()

        s += '}'
        return s

    def edges_string(self):
        s = ''
        for child in self.successors:
            s += child.edges_string()

        if self.predecessor is None: return s
        pred_type = 'Bag' if self.predecessor.is_bag else 'Edge'
        node_type = 'Bag' if self.is_bag else 'Edge'
        s += f'{pred_type} {self.predecessor.id} -> {node_type} {self.id}\n'
        return s

    def __str__(self):
        s = ''
        # assert self.successors is not None or self.status == UNKNOWN
        for child in self.successors:
            s += str(child)

        node_type = 'Bag' if self.is_bag else 'Edge'
        s += f'The status at {node_type} {self.id} is {self.status}.\n'
        s += f'The chosen successor at {node_type} {self.id} is {self.strategy}.\n'
        s += f'The subgraph at {node_type} {self.id} is\n{self.subgraph}\n'
        return s

'''
    Returns a pair of the search tree and a boolean indicating whether the search tree contains a valid
    tree decomposition.
'''
def compute_tree_decomposition(split_graph, maximum_bag_size):
    global root_graph
    root_graph = split_graph
    node = DecompositionNode(pred=None, labelled_subgraph=split_graph, is_bag=True)
    node.decompose_subgraph()
    while 1:
        if node.is_bag:
            bag = node

            # quit on failure because we need every component to work out
            for edge in bag.successors:
                if edge.status == FAILED:
                    bag.status = FAILED
                    bag.strategy = edge
                    break

            if bag.status == FAILED:
                if bag.predecessor is None: return bag, False
                node = bag.predecessor
                for edge in bag.successors:
                    edge.delete()
                continue

            unknown_bag_edges = [edge for edge in bag.successors if edge.status == UNKNOWN]
            if unknown_bag_edges:
                unknown_subgraphs = [edge.subgraph for edge in unknown_bag_edges]
                index = choose_weakest_component(unknown_subgraphs)
                node = unknown_bag_edges[index]
            else:
                bag.set_status(SUCCESS)
                if bag.predecessor is None: return bag, True
                node = bag.predecessor
        else:
            edge = node

            # quit on success because we only need some cop to work
            for bag in edge.successors:
                if bag.status == SUCCESS:
                    edge.status = SUCCESS
                    edge.strategy = bag
                    break

            if edge.status == SUCCESS:
                # the predecessor of an edge will never be None because the single root is a bag
                node = edge.predecessor
                continue

            known_cops = [bag.subgraph.new_cop for bag in edge.successors]
            choosable_cops = compute_choosable_cops(edge.subgraph, known_cops, maximum_bag_size)
            if choosable_cops:
                index = choose_strongest_cop(edge.subgraph, choosable_cops)

                # create a new bag on the fly
                cop = choosable_cops[index]
                split_subgraph = edge.subgraph.copy()
                split_subgraph.place(cop)
                child = DecompositionNode(pred=edge, labelled_subgraph=split_subgraph, is_bag=True)
                child.decompose_subgraph()
                edge.add_child(child)

                node = child
            else:
                edge.set_status(FAILED)
                node = edge.predecessor
    return None

'''
    Choose a component that is most likely to fail to decompose with the given maximum bag size
    The given list of labelled subgraphs is not empty.
'''
def choose_weakest_component(unknown_subgraphs):
    return len(unknown_subgraphs)-1

'''
    Choose a cop that is most likely to succeed to decompose with the given maximum bag size
    The given list of choosable cops is not empty.
'''
def choose_strongest_cop(subgraph, unknown_cops):
    return 0

def compute_choosable_cops(escape_component, known_cops, maximum_bag_size):
    choosable = []
    if len(escape_component.cops) >= maximum_bag_size:
        return choosable
    for vertex in escape_component.adjacent:
        if not escape_component.is_cop(vertex) and vertex not in known_cops:
            choosable.append(vertex)
    return choosable

def parse_graph(filepath):
    graph = Graph()
    with open(filepath) as file:
        for line in file:
            if line[0] == 'c':
                continue
            if line[0] == 'p':
                continue
            edge = line.split(' ')
            tail, head = int(edge[0]), int(edge[1])
            if tail not in graph.adjacent:
                graph.adjacent[tail] = []
            graph.adjacent[tail].append(head)
    return graph

if __name__ == '__main__':
    treewidth = int(argv[1])
    filepath = argv[2]
    dot_filepath = argv[3]
    G = parse_graph(filepath)
    G.make_symmetric()

    logging.info(f'We want a tree decomposition of width {treewidth} for the following graph:\n{G}')
    search_tree, success = compute_tree_decomposition(G, treewidth+1)
    if success:
        logging.info('Successfully computed a tree decomposition.')
        logging.debug(str(search_tree))
        logging.debug(search_tree.edges_string())
    else:
        logging.error('Failed computing a tree decomposition.')

    tree_dot_string = search_tree.dot_string()
    with open(dot_filepath, 'w') as f:
        print(tree_dot_string, file=f)

    tree_decomposition = search_tree.extract_tree_decomposition()
    logging.debug('Following tree decomposition has been found')
    logging.debug(str(tree_decomposition))
