from random import choice, seed
import logging
from graph import Graph, decompose_into_connected_components
from sys import argv

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

UNKNOWN = 0
FAILED = 1
SUCCESS = 2

class DecompositionNode:

    def __init__(self, pred, labelled_subgraph, is_bag):
        self.predecessor = pred
        self.subgraph = labelled_subgraph
        self.successors = None
        self.is_bag = is_bag
        self.strategy = None
        self.status = UNKNOWN

    def add_child(self, child):
        self.successors.append(child)

    def set_status(self, new_status):
        self.status = new_status

'''
    Returns a pair of the search tree and a boolean indicating whether the search tree contains a valid
    tree decomposition.
'''
def compute_tree_decomposition(split_graph, maximum_bag_size):
    node = DecompositionNode(pred=None, labelled_subgraph=split_graph, is_bag=True)
    while 1:
        if node.is_bag:
            bag = node

            # add all required successor bag edges
            if bag.successors is None:
                bag.successors = []

                components = decompose_into_connected_components(bag.subgraph)
                for comp in components:
                    child = DecompositionNode(pred=bag, labelled_subgraph=comp, is_bag=False)
                    bag.add_child(child)

            # quit on failure because we need every component to work out
            for edge in bag.successors:
                if edge.status == FAILED:
                    bag.status = FAILED
                    bag.strategy = edge
                    break

            if bag.status == FAILED:
                if bag.predecessor is None: return bag, False
                node = bag.predecessor
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

            if edge.successors is None:
                edge.successors = []

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
    G = parse_graph(filepath)
    G.make_symmetric()

    logging.info(f'We want a tree decomposition of width {treewidth} for the following graph:\n{G}')
    search_tree, success = compute_tree_decomposition(G, treewidth+1)
    if success:
        logging.info('Successfully computed a tree decomposition.')
        # logging.debug(search_tree.edges_string())
        # logging.debug(str(search_tree))
    else:
        logging.error('Failed computing a tree decomposition.')

    # tree_dot_string = search_tree.dot_string()
    # with open('generated.dot', 'w') as f:
    #     print(tree_dot_string, file=f)
