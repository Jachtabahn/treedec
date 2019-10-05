import logging
import graph
import treedec
import argparse
from os import path

UNKNOWN = 0
FAILED = 1
SUCCESS = 2

'''
    This is the root graph, that is decomposed into a tree. It's used in DecompositionNode.write_subgraph_dots(), when inside
    each search tree node, I draw the entire graph and then blend out the parts I don't need, so that the subgraphs are
    more comparable.
'''
root_graph = None

num_nodes = 0
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
        components = graph.decompose_into_connected_components(self.subgraph)
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
        tree_decomposition = treedec.TreeDecomposition(self.subgraph.cops, self.id, children)
        return tree_decomposition

    def write_subgraph_dots(self):
        dot = ''
        shell = ''
        for child in self.successors:
            child_dot, child_shell = child.write_subgraph_dots()
            dot += child_dot
            shell += child_shell

        node_name = f'b{self.id}' if self.is_bag else f'e{self.id}'
        shell += f'dot -Tsvg -o svg/{node_name}.svg dot/{node_name}.dot\n'
        graph_dot = self.subgraph.dot_string(root_graph)
        graph_dot_path = f'dot/{node_name}.dot'
        with open(graph_dot_path, 'w') as f:
            f.write(graph_dot)

        if self.is_bag:
            node_color = '#ff8c00b2'
        else:
            node_color = '#00ced172'
        status_color = {
            UNKNOWN: 'gray',
            FAILED: 'crimson',
            SUCCESS: 'green3'
        }

        dot += f'{node_name} [label="", penwidth=6, '
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

    def write_dot(self, graph_name):
        dot = 'digraph {\n'
        dot += 'edge [penwidth=3]\n'
        dot += 'node [style=filled, color=aliceblue]\n'
        dot_nodes_string, shell = self.write_subgraph_dots()
        dot += dot_nodes_string
        dot += '}'
        with open(f'dot/{graph_name}.dot', 'w') as f:
            f.write(dot)

        shell += f'\ndot -Tsvg -o svg/{graph_name}.svg dot/{graph_name}.dot\n'
        shell += f'inkscape svg/{graph_name}.svg\n'
        with open(f'visualize-{graph_name}.sh', 'w') as f:
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
    input_graph = graph.parse_graph(graph_path)
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
    search_tree.write_dot(graph_name)

    # extract the found tree decomposition from the constructed search tree
    tree_decomposition = search_tree.extract_tree_decomposition()
    if not tree_decomposition.validate(input_graph):
        logging.error('I computed an invalid tree decomposition.')
        return None
    logging.info(f'I found a valid tree decomposition of width at most {maximum_bag_size-1}.')
    logging.debug(tree_decomposition)

    # save the computed tree decomposition
    tree_decomposition.save(graph_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--maximum-bag-size', '-b', type=int)
    parser.add_argument('--graph-path', '-g')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    search_for_tree_decomposition(args.maximum_bag_size, args.graph_path)
