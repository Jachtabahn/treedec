import logging
import network
import treedec
import argparse
from os import path
import sys
import json

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

    def write_subnet_dots(self, prefix):
        dot = ''
        shell = ''
        for child in self.successors:
            child_dot, child_shell = child.write_subnet_dots(prefix)
            dot += child_dot
            shell += child_shell

        logging.debug(f"Writing dot file for node {self.id}")

        node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
        shell += f'dot -Tsvg -o svg/{node_name}.svg dot/{node_name}.dot\n'
        network_dot = self.subnet.visualize()
        graph_dot_path = f'dot/{node_name}.dot'
        with open(f'{prefix}/{graph_dot_path}', 'w') as f:
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

    def write_dot(self, network_name, prefix='.'):
        dot = 'digraph {\n'
        dot += 'edge [penwidth=3]\n'
        dot += 'node [style=filled, color=aliceblue]\n'
        dot_nodes_string, shell = self.write_subnet_dots(prefix)
        dot += dot_nodes_string
        dot += '}'
        with open(f'{prefix}/dot/{network_name}.dot', 'w') as f:
            f.write(dot)

        shell += f'\ndot -Tsvg -o svg/{network_name}.svg dot/{network_name}.dot\n'
        shell += f'inkscape svg/{network_name}.svg\n'
        with open(f'{prefix}/visualize-{network_name}.sh', 'w') as f:
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
def compute_tree_decomposition(split_graph, fixed_treewidth, fixed_joinwidth):
    node = DecompositionNode(pred=None, labelled_subnet=split_graph, is_bag=True)
    node.decompose_subgraph()
    logging.debug(f'Input network has {len(node.successors)} connected components.')
    while 1:
        if node.is_bag:
            bag = node

            # quit on failure, because we need every component to work out
            for edge in bag.successors:
                if edge.status == FAILED:
                    bag.status = FAILED
                    bag.strategy = edge
                    break

            if bag.status == FAILED:
                if bag.predecessor is None: return bag, False
                node = bag.predecessor
                # this does not always delete all edges of this bag, see steps 69-73 for ClebschGraph
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

            # quit on success, because we only need some cop to work
            for bag in edge.successors:
                if bag.status == SUCCESS:
                    edge.status = SUCCESS
                    edge.strategy = bag
                    break

            if edge.status == SUCCESS:
                # the predecessor of an edge will never be None, because the single root is a bag
                node = edge.predecessor
                continue

            escape_component = edge.subnet
            known_cops = [bag.subnet.new_cop for bag in edge.successors]
            choosable_cops = compute_choosable_cops(escape_component, known_cops, fixed_treewidth, fixed_joinwidth)
            if choosable_cops:
                cop = choose_strongest_cop(escape_component, choosable_cops)

                # create a new bag on the fly
                split_subgraph = escape_component.copy()
                split_subgraph.place(cop)
                bag_child = DecompositionNode(pred=edge, labelled_subnet=split_subgraph, is_bag=True)
                bag_child.decompose_subgraph()
                edge.add_child(bag_child)

                node = bag_child
            else:
                edge.set_status(FAILED)
                node = edge.predecessor

    # unreachable

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
def choose_strongest_cop(subnet, choosable_cops):
    # Without this check: in ClebschGraph.gr, Bag 46865 is a bag with a new cop that is not adjacent to any old cop
    # We want to not consider bags, where the new cop is not adjacent to any old cop
    # for i, cop_vertex in enumerate(choosable_cops):
    #     if not set(subnet.adjacent[cop_vertex]).isdisjoint(subnet.cops):
    #         return i
    return choosable_cops[0]

def compute_choosable_cops(escape_component, known_cops, fixed_treewidth, fixed_joinwidth):
    my_treewidth = len(escape_component.cops) - 1
    if my_treewidth >= fixed_treewidth: return []
    choosable = []
    for vertex in escape_component.adjacent:
        if escape_component.is_cop(vertex) or vertex in known_cops:
            continue

        # create a new bag on the fly
        split_subgraph = escape_component.copy()
        split_subgraph.place(vertex)
        bag_child = DecompositionNode(pred=None, labelled_subnet=split_subgraph, is_bag=True)
        bag_child.decompose_subgraph()

        # this bag always has a predecessor bag, because this bag is attached to an edge
        bag_degree = len(bag_child.successors) + 1
        if bag_degree >= 3:
            # + 1 because of the newly placed vertex
            my_joinwidth = my_treewidth + 1
        else:
            my_joinwidth = -1

        if my_joinwidth <= fixed_joinwidth:
            choosable.append(vertex)
    return choosable

def search_for_tree_decomposition(network_name, treewidths_json, fixed_treewidth, fixed_joinwidth, treedec_path):
    input_network = network.parse(sys.stdin)

    if fixed_treewidth is None:
        logging.info('Did not fix the treewidth directly.')

        if treedec_path is None:
            if treewidths_json is None or not path.exists(treewidths_json):
                logging.error('The treewidths database path is invalid!')
                return False

            with open(treewidths_json) as file:
                treewidths_database = json.load(file)
            if network_name not in treewidths_database:
                logging.error(f'Did not find network {network_name} in the treewidths database {treewidths_json}.')
                return False
            fixed_treewidth = treewidths_database[network_name]
        else:
            with open(treedec_path) as f:
                my_treedec = treedec.parse(f)
                my_treedec.collect_info()
                fixed_treewidth = my_treedec.treewidth

        # See what happens, when I increase the treewidth by one and decrease the joinwidth by one
        fixed_joinwidth = fixed_treewidth
        if fixed_treewidth > 1:
            fixed_treewidth += 1
            fixed_joinwidth -= 1

        logging.info(f'Extracted treewidth {fixed_treewidth}')

    if fixed_joinwidth is None:
        logging.warning(f'Joinwidth not fixed; setting to {fixed_treewidth}')
        fixed_joinwidth = fixed_treewidth

    logging.info(f'Initiating search for a tree decomposition of width at most {fixed_treewidth} for following network.\n{input_network}')
    input_network.make_symmetric()

    logging.info(f'Treewidth is fixed to {fixed_treewidth}.')
    logging.info(f'Joinwidth is fixed to {fixed_joinwidth}.')
    search_tree, success = compute_tree_decomposition(input_network, fixed_treewidth, fixed_joinwidth)
    if not success:
        logging.info(f'Failed computing a tree decomposition of width at most {fixed_treewidth}.')
        return False

    # extract the found tree decomposition from the constructed search tree
    tree_decomposition = search_tree.extract_tree_decomposition()
    if not tree_decomposition.validate(input_network):
        logging.error(f'Computed an invalid tree decomposition!')
        return False
    logging.info(f'Found a valid tree decomposition of width at most {fixed_treewidth}.')
    logging.debug(tree_decomposition)

    # save the computed tree decomposition
    tree_decomposition.save(sys.stdout)
    logging.info('Computed tree decomposition has been output.')
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network-name', '-g', default=None)
    parser.add_argument('--treewidths-json', '-t', type=str, default=None)
    parser.add_argument('--fixed-treewidth', '-w', type=int, default=None)
    parser.add_argument('--fixed-joinwidth', '-j', type=int, default=None)
    parser.add_argument('--treedec-path', '-d', type=str, default=None)
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

    success = search_for_tree_decomposition(
        args.network_name,
        args.treewidths_json,
        args.fixed_treewidth,
        args.fixed_joinwidth,
        args.treedec_path)

    if not success:
        exit(1)
