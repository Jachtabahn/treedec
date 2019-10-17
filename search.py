import logging
import network
import treedec
import argparse
from os import path
import sys

UNKNOWN = 0
FAILED = 1
SUCCESS = 2

num_nodes = 0
class DecompositionNode:

    def __init__(self, pred, labelled_subnet, is_bag):
        self.predecessor = pred
        self.subnet = labelled_subnet
        self.successors = []
        self.is_bag = is_bag
        self.strategy = None
        self.status = UNKNOWN
        self.treewidth = None
        self.joinwidth = None

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
        components = network.decompose_into_connected_components(self.subnet)
        for comp in components:
            edge_child = DecompositionNode(pred=self, labelled_subnet=comp, is_bag=False)
            self.add_child(edge_child)

    def extract_tree_decomposition(self):
        if self.strategy is not None:
            return self.strategy.extract_tree_decomposition()
        children = []
        for succ in self.successors:
            child_decomposition = succ.extract_tree_decomposition()
            children.append(child_decomposition)
        tree_decomposition = treedec.TreeDecomposition(
            bag=self.subnet.cops,
            tree_id=self.id,
            children=children,
            treewidth=self.treewidth,
            joinwidth=self.joinwidth)
        return tree_decomposition

    def write_subnet_dots(self):
        dot = ''
        shell = ''
        for child in self.successors:
            child_dot, child_shell = child.write_subnet_dots()
            dot += child_dot
            shell += child_shell

        node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
        shell += f'dot -Tsvg -o svg/{node_name}.svg dot/{node_name}.dot\n'
        network_dot = self.subnet.visualize()
        graph_dot_path = f'dot/{node_name}.dot'
        with open(graph_dot_path, 'w') as f:
            f.write(network_dot)

        if self.is_bag:
            node_color = '#ff8c00b2'
            node_label = f'Bag {self.id}'
        else:
            node_color = '#00ced172'
            node_label = f'Edge {self.id}'
        status_color = {
            UNKNOWN: 'gray',
            FAILED: 'crimson',
            SUCCESS: 'green3'
        }

        dot += f'{node_name} [label="{node_label}", penwidth=6, '
        dot += 'shape=rectangle, '
        dot += f'color={status_color[self.status]}, '
        dot += f'fillcolor="{node_color}", '
        graph_svg_path = graph_dot_path.replace('dot', 'svg')
        dot += f'image="{graph_svg_path}"]\n'

        if self.predecessor is not None:
            pred_name = f'b{self.predecessor.id}' if self.predecessor.is_bag else f'e{self.predecessor.id}'
            color = f' [color=green]' if self == self.predecessor.strategy else ''
            dot += f'{pred_name} -> {node_name}{color}\n'

        return dot, shell

    def write_dot(self, network_name):
        dot = 'digraph {\n'
        dot += 'edge [penwidth=3]\n'
        dot += 'node [style=filled, color=aliceblue]\n'
        dot_nodes_string, shell = self.write_subnet_dots()
        dot += dot_nodes_string
        dot += '}'
        with open(f'dot/{network_name}.dot', 'w') as f:
            f.write(dot)

        shell += f'\ndot -Tsvg -o svg/{network_name}.svg dot/{network_name}.dot\n'
        shell += f'inkscape svg/{network_name}.svg\n'
        with open(f'visualize-{network_name}.sh', 'w') as f:
            f.write(shell)
        return dot

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
        s += f'The subnet at {node_type} {self.id} is\n{self.subnet}\n'
        return s

'''
    Returns a pair of the search tree and a boolean indicating whether the search tree contains a valid
    tree decomposition.
'''
def compute_tree_decomposition(split_graph, maximum_bag_size):
    node = DecompositionNode(pred=None, labelled_subnet=split_graph, is_bag=True)
    node.decompose_subgraph()
    logging.debug(f'Input network has {len(node.successors)} connected components.')
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
                unknown_subgraphs = [edge.subnet for edge in unknown_bag_edges]
                index = choose_weakest_component(unknown_subgraphs)
                node = unknown_bag_edges[index]
            else:
                bag.set_status(SUCCESS)

                # determine the number of neighbours of this bag
                bag_degree = len(bag.successors)
                if bag.predecessor is not None:
                    bag_degree += 1

                # determine the treewidth for the tree under this bag
                my_treewidth = len(bag.subnet.cops)-1
                if bag_degree >= 3:
                    my_joinwidth = my_treewidth
                else:
                    my_joinwidth = -1
                for edge in bag.successors:
                    next_bag = edge.strategy
                    my_treewidth =  max(my_treewidth, next_bag.treewidth)
                    my_joinwidth =  max(my_joinwidth, next_bag.joinwidth)
                bag.treewidth = my_treewidth
                bag.joinwidth = my_joinwidth

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

            known_cops = [bag.subnet.new_cop for bag in edge.successors]
            choosable_cops = compute_choosable_cops(edge.subnet, known_cops, maximum_bag_size)
            if choosable_cops:
                index = choose_strongest_cop(edge.subnet, choosable_cops)

                # create a new bag on the fly
                cop = choosable_cops[index]
                split_subgraph = edge.subnet.copy()
                split_subgraph.place(cop)
                bag_child = DecompositionNode(pred=edge, labelled_subnet=split_subgraph, is_bag=True)
                bag_child.decompose_subgraph()
                edge.add_child(bag_child)

                node = bag_child
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
def choose_strongest_cop(subnet, unknown_cops):
    # Without this check: in ClebschGraph.gr, Bag 46865 is a bag with a new cop that is not adjacent to any old cop
    # We want to not consider bags, where the new cop is not adjacent to any old cop
    for i, cop_vertex in enumerate(unknown_cops):
        if not set(subnet.adjacent[cop_vertex]).isdisjoint(subnet.cops):
            return i
    return 0

def compute_choosable_cops(escape_component, known_cops, maximum_bag_size):
    choosable = []
    if len(escape_component.cops) >= maximum_bag_size:
        return choosable
    for vertex in escape_component.adjacent:
        if not escape_component.is_cop(vertex) and vertex not in known_cops:
            choosable.append(vertex)
    return choosable

def search_for_tree_decomposition(network_name, given_maximum_bag_size, precomputed_treedec_path):
    input_network = network.parse(sys.stdin)

    if given_maximum_bag_size is None and precomputed_treedec_path is None:
        logging.error('Please provide a maximum bag size or a path to a precomputed tree decomposition, where to find the max. bag size')
        exit(1)
    if given_maximum_bag_size is not None:
        maximum_bag_size = given_maximum_bag_size
        logging.info(f'Using the provided max. bag size {maximum_bag_size}')
    else:
        maximum_bag_size = treedec.extract_bag_size(precomputed_treedec_path)
        if maximum_bag_size is None:
            logging.error(f'Failed to extract the maximum bag size from path {precomputed_treedec_path}')
            exit(1)
        logging.info(f'Extracted the max. bag size {maximum_bag_size}')

    logging.info(f'I initiate search for a tree decomposition of width at most {maximum_bag_size-1} for the network:\n{input_network}')
    input_network.make_symmetric()

    # search for a tree decomposition
    search_tree, success = compute_tree_decomposition(input_network, maximum_bag_size)
    if not success:
        logging.error('I failed computing a tree decomposition.')
        return None

    # visualize the computed search tree
    if network_name is not None:
        search_tree.write_dot(network_name)

    # extract the found tree decomposition from the constructed search tree
    tree_decomposition = search_tree.extract_tree_decomposition()
    if not tree_decomposition.validate(input_network):
        logging.error('I computed an invalid tree decomposition.')
        return None
    logging.info(f'I found a valid tree decomposition of width at most {maximum_bag_size-1}.')
    logging.debug(tree_decomposition)

    # save the computed tree decomposition
    tree_decomposition.save(sys.stdout)

    # visualize the input network and the computed tree decomposition
    # if network_name is not None:
    #     input_network.write_dot(network_name)
    #     tree_decomposition.write_dot(network_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network-name', '-g', default=None)
    parser.add_argument('--maximum-bag-size', '-b', type=int, default=None)
    parser.add_argument('--precomputed-treedec-path', '-w', type=str, default=None)
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    search_for_tree_decomposition(args.network_name, args.maximum_bag_size, args.precomputed_treedec_path)
