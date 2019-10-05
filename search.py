import logging
from graph import decompose_into_connected_components, parse_graph
from sys import argv
from tree_decomposition import TreeDecomposition

logging.basicConfig(format='%(message)s', level=logging.INFO)

UNKNOWN = 0
FAILED = 1
SUCCESS = 2

num_nodes = 0

'''
    This is the root graph, that is decomposed into a tree. It's used in DecompositionNode.dot_nodes(), when inside
    each cluster, I draw the entire graph and then blend out the parts I don't need, so that the subgraphs are
    more comparable. But actually, this doesn't necessarily make them look similar, and it might still
    happen, that some nodes or edges get drawn differently.

    Additionally, drawing graphs inside the clusters breaks
    the whole layout, and clusters and their edges are drawn chaotically. When the clusters are empty and
    have no graphs inside them, the layout is a clean and beautiful tree.
'''
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
        if self.strategy is not None:
            return self.strategy.extract_tree_decomposition()
        children = []
        for succ in self.successors:
            child_decomposition = succ.extract_tree_decomposition()
            children.append(child_decomposition)
        tree_decomposition = TreeDecomposition(self.subgraph.cops, self.id, children)
        return tree_decomposition

    def dot_nodes(self):
        s = ''
        for child in self.successors:
            s += child.dot_nodes()

        node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
        graph_dot = self.subgraph.dot_string(root_graph)
        with open(f'dot/{node_name}.dot') as f:
            f.write(graph_dot)

        color = bag_color if self.is_bag else edge_color
        node_label = f'Bag {self.id}' if self.is_bag else f'Edge {self.id}'
        edge_color = '#00ced172'
        bag_color = '#ff8c00b2'
        status_color = {
            UNKNOWN: 'gray',
            FAILED: 'crimson',
            SUCCESS: 'green3'
        }

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

        s += self.dot_nodes()

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

def search_for_tree_decomposition(maximum_bag_size, graph_path):
    # parse input graph
    input_graph = parse_graph(graph_path)
    graph_dir, graph_name = path.split(graph_path)
    graph_name = graph_name.replace('.gr', '')
    logging.info(f'I am looking for a tree decomposition of width <= {maximum_bag_size-1} for the graph:\n{input_graph}')
    input_graph.make_symmetric()

    # search for a tree decomposition
    search_tree, success = compute_tree_decomposition(input_graph, maximum_bag_size)
    if not success:
        logging.error('I failed computing a tree decomposition.')
        return None

    # save the computed search tree
    search_dot_path = f'dot/{graph_name}.dot'
    with open(search_dot_path, 'w') as f:
        search_tree_string = search_tree.dot_string()
        f.write(search_tree_string)

    # extract the found tree decomposition from the constructed search tree
    tree_decomposition = search_tree.extract_tree_decomposition()
    if not tree_decomposition.validate(input_graph):
        logging.error('I computed an invalid tree decomposition.')
        return None
    logging.info(f'I found a valid tree decomposition of width at most {maximum_bag_size-1}.')
    logging.debug(tree_decomposition)

    # save the computed tree decomposition
    treedec_path = f'treedecs/{graph_name}.td'
    with open(treedec_path, 'w') as f:
        tree_string = tree_decomposition.output_format()
        f.write(tree_string)

if __name__ == '__main__':
    search_for_tree_decomposition(int(argv[1]), argv[2])
