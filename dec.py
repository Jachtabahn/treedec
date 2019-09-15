from random import choice, seed
import logging
from graph import Graph, decompose_into_connected_components

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

STATUS_UNKNOWN = 0
STATUS_FAILED = 1
STATUS_SUCCESS = 2

class SearchTree:

    def __init__(self, split_graph):
        self.predecessor = {0: None}
        self.subgraph = {0: split_graph}

        self.successors = {0: None}
        self.unprocessed_successors = {0: None}
        self.is_bag = {0: True}
        self.chosen_successor = {0: None}
        self.status = {0: STATUS_UNKNOWN}
        self.num_nodes = 1

    def delete(self, node):
        if node not in self.successors: return
        deletable_successors = self.successors[node] if self.successors[node] is not None else []
        for succ in deletable_successors:
            self.delete(succ)

        pred = self.predecessor[node]
        self.successors[pred].remove(node)
        if self.chosen_successor[pred] == node:
            self.chosen_successor[pred] = None

        del self.predecessor[node]
        del self.subgraph[node]
        del self.successors[node]
        del self.unprocessed_successors[node]
        del self.is_bag[node]
        del self.chosen_successor[node]
        del self.status[node]
        self.num_nodes -= 1

    def add(self, node, labelled_subgraph):
        new_node = self.num_nodes
        self.predecessor[new_node] = node
        self.subgraph[new_node] = labelled_subgraph

        self.successors[new_node] = None
        self.unprocessed_successors[new_node] = None
        self.is_bag[new_node] = not self.is_bag[node]
        self.chosen_successor[new_node] = None
        self.status[new_node] = STATUS_UNKNOWN

        self.successors[node].append(new_node)
        self.unprocessed_successors[node].append(new_node)
        self.num_nodes += 1

    def set_status(self, node, status):
        self.status[node] = status

    def get_predecessor(self, node):
        return self.predecessor[node]

    def mark_processed(self, pred, node):
        self.unprocessed_successors[pred].remove(node)

    def get_subgraph(self, node):
        return self.subgraph[node]

    def get_root(self):
        return 0

    def nodes(self):
        return list(self.successors.keys())

    def dot_string(self):
        s = 'digraph {\n'
        s += 'graph [compound=true, ranksep=1, nodesep=1]\n'
        s += 'edge [penwidth=3]\n'
        s += 'node [style=filled, color=aliceblue]\n'

        edge_color = '#00ced172'
        bag_color = '#ff8c00b2'
        status_color = {
            STATUS_UNKNOWN: 'gray',
            STATUS_FAILED: 'crimson',
            STATUS_SUCCESS: 'green3'
        }
        root_graph = self.subgraph[self.get_root()]
        for node, node_subgraph in self.subgraph.items():
            is_bag_node = self.is_bag[node]
            color = bag_color if is_bag_node else edge_color
            node_name = f'b{node}' if is_bag_node else f'e{node}'
            node_label = f'Bag {node}' if is_bag_node else f'Edge {node}'

            s += f'subgraph cluster_{node_name} '
            s += '{\n'
            s += f'graph [label="{node_label}", style=rounded, '
            node_status = self.status[node]
            s += f'bgcolor="{color}", penwidth=8, color={status_color[node_status]}]\n'
            s += 'edge [penwidth=1, dir=none]\n'
            s += f'{node_name} [style=invis]\n'
            subgraph_string = node_subgraph.dot_string(node_name, root_graph)
            s += subgraph_string
            s += '}\n'

        chosen_color = 'red'
        for node, pred in self.predecessor.items():
            if pred is None: continue

            node_name = f'b{node}' if self.is_bag[node] else f'e{node}'
            pred_name = f'b{pred}' if self.is_bag[pred] else f'e{pred}'
            color = f', color={chosen_color}' if self.chosen_successor[pred] == node else ''

            s += f'{pred_name} -> {node_name} [ltail=cluster_{pred_name}, '
            s += f'lhead=cluster_{node_name}{color}]\n'

        s += '}'
        return s

    def edges_string(self):
        s = ''
        for node in self.nodes():
            pred = self.predecessor[node]
            if pred is None: continue
            pred_type = 'Bag' if self.is_bag[pred] else 'Edge'
            node_type = 'Bag' if self.is_bag[node] else 'Edge'
            s += f'{pred_type} {pred} -> {node_type} {node}\n'
        return s

    def __str__(self):
        s = ''
        for node in self.nodes():
            node_type = 'Bag' if self.is_bag[node] else 'Edge'
            s += f'The status at {node_type} {node} is {self.status[node]}\n'
            s += f'The chosen successor at {node_type} {node} is {self.chosen_successor[node]}\n'
            s += f'The subgraph at {node_type} {node} is\n{self.subgraph[node]}'
        return s
'''
    Returns a pair of the search tree and a boolean indicating whether the search tree contains a valid
    tree decomposition.
'''
def compute_tree_decomposition(split_graph, maximum_bag_size):
    search_tree = SearchTree(split_graph)
    node = search_tree.get_root()
    while 1:
        if search_tree.is_bag[node]:
            # add all required successor bag edges
            if search_tree.successors[node] is None:
                search_tree.successors[node] = []
                search_tree.unprocessed_successors[node] = []

                node_subgraph = search_tree.get_subgraph(node)
                components = decompose_into_connected_components(node_subgraph)
                for comp in components:
                    search_tree.add(node, comp)

            # quit on failure because we need every component to work out
            if search_tree.status[node] == STATUS_FAILED:
                pred = search_tree.get_predecessor(node)
                if pred is None: return search_tree, False
                search_tree.mark_processed(pred, node)
                node = pred
                continue

            # choose some unworked successor
            unknown_bag_edges = [succ for succ in search_tree.unprocessed_successors[node] \
                if search_tree.status[succ] == STATUS_UNKNOWN]
            if not unknown_bag_edges:
                search_tree.set_status(node, STATUS_SUCCESS)
                pred = search_tree.get_predecessor(node)
                if pred is None: return search_tree, True
                search_tree.mark_processed(pred, node)
                search_tree.set_status(pred, STATUS_SUCCESS)
                search_tree.chosen_successor[pred] = node
                node = pred
            else:
                unknown_subgraphs = [search_tree.get_subgraph(succ) for succ in unknown_bag_edges]
                index = choose_weakest_component(unknown_subgraphs)
                node = unknown_bag_edges[index]
        else:
            # add all possible successor bags
            if search_tree.successors[node] is None:
                search_tree.successors[node] = []
                search_tree.unprocessed_successors[node] = []

                escape_component = search_tree.get_subgraph(node)
                choosable_cops = compute_choosable_cops(escape_component, maximum_bag_size)
                for cop in choosable_cops:
                    new_subgraph = escape_component.copy()
                    new_subgraph.place(cop)
                    search_tree.add(node, new_subgraph)

            # quit on success because we only need some cop to work
            if search_tree.status[node] == STATUS_SUCCESS:
                pred = search_tree.get_predecessor(node)
                if pred is None: return search_tree, True
                search_tree.mark_processed(pred, node)
                node = pred
                continue

            # choose some unworked successor
            unknown_bags = [succ for succ in search_tree.unprocessed_successors[node] \
                if search_tree.status[succ] == STATUS_UNKNOWN]
            if not unknown_bags:
                pred = search_tree.get_predecessor(node)
                assert pred is not None # because the root is always a bag

                # clear memory
                for failed_edge in search_tree.successors[pred]:
                    search_tree.delete(failed_edge)

                search_tree.set_status(node, STATUS_FAILED)
                search_tree.mark_processed(pred, node)
                search_tree.set_status(pred, STATUS_FAILED)
                search_tree.chosen_successor[pred] = node
                node = pred
            else:
                unknown_cops = [search_tree.get_subgraph(succ).new_cop for succ in unknown_bags]
                index = choose_strongest_cop(search_tree.get_subgraph(node), unknown_cops)
                node = unknown_bags[index]
    return None

'''
    The given list of labelled subgraphs is not empty.
'''
def choose_weakest_component(unknown_subgraphs):
    return len(unknown_subgraphs)-1

'''
    The given list of labelled subgraphs is not empty.
'''
def choose_strongest_cop(subgraph, unknown_cops):
    return 0

def compute_choosable_cops(escape_component, maximum_bag_size):
    choosable = []
    if len(escape_component.cops) >= maximum_bag_size:
        return choosable
    for node in escape_component.nodes():
        if not escape_component.is_cop(node):
            choosable.append(node)
    return choosable

if __name__ == '__main__':
    # non-trivial graph on 14 vertices
    # G = Graph({
    #     1: [2, 3, 4],
    #     2: [5, 8],
    #     3: [7, 8],
    #     4: [9, 10],
    #     5: [11, 12],
    #     6: [13, 14],
    #     7: [11, 13],
    #     8: [12, 14],
    #     9: [11, 14],
    #     10: [12, 13]
    # })

    # trivial forest on 7 vertices
    G = Graph({
        1: [2, 5],
        2: [3, 4],
        6: [7]
    })
    G.make_symmetric()
    k = 2

    logging.info(f'We want a tree decomposition of width {k-1} for the following graph:\n{G}')
    search_tree, success = compute_tree_decomposition(G, k)
    if success:
        logging.info('Successfully computed a tree decomposition.')
        logging.debug(search_tree.edges_string())
        logging.debug(str(search_tree))
    else:
        logging.error('Failed computing a tree decomposition.')

    tree_dot_string = search_tree.dot_string()
    with open('generated.dot', 'w') as f:
        print(tree_dot_string, file=f)
