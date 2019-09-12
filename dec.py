from random import choice, seed
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

class Graph:

    def __init__(self, adjacent=None, cops=None):
        self.adjacent = adjacent if adjacent is not None else dict()
        self.cops = cops if cops is not None else []
        self.new_cop = None

    def nodes(self):
        return list(self.adjacent.keys())

    def copy(self):
        copied_adjacent = dict()
        for node, neighbours in self.adjacent.items():
            copied_adjacent[node] = list(neighbours)
        copied = Graph(copied_adjacent, list(self.cops))
        return copied

    def add(self, node, neighbours, is_cop):
        assert node not in self.adjacent
        self.adjacent[node] = neighbours
        if is_cop:
            assert node not in self.cops
            self.cops.append(node)

    def place(self, n):
        if n not in self.cops:
            self.cops.append(n)
            self.new_cop = n

    def is_cop(self, n):
        return n in self.cops

    def make_symmetric(self):
        for node, neighbours in list(self.adjacent.items()):
            for neigh in neighbours:
                if neigh not in self.adjacent:
                    self.adjacent[neigh] = [node]
                elif node not in self.adjacent[neigh]:
                    self.adjacent[neigh].append(node)

    def __str__(self):
        s = '----------- Graph -----------\n'
        for n, a in self.adjacent.items():
            if not self.is_cop(n):
                s += f'Robber {n}: {a}\n'
            else:
                s += f'Cop    {n}: {a}\n'
        return s

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
                    failed_bags = search_tree.successors[failed_edge]
                    if failed_bags is None: continue
                    for failed_bag in failed_bags:
                        search_tree.delete(failed_bag)

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
    if len(escape_component.cops) >= maximum_bag_size:
        return []
    if len(escape_component.cops) == 0:
        return list(escape_component.nodes())
    choosable = []
    for node in escape_component.nodes():
        if escape_component.is_cop(node):
            neighbours = escape_component.adjacent[node]
            choosable += [neigh for neigh in neighbours if not escape_component.is_cop(neigh)]
    return choosable

'''
    Decomposes a given graph minus its cop nodes into connected subgraphs, where each subgraph still contains
    those cops that surround it. So we take a graph, remove all the cop nodes and that gives us a copless subgraph.
    Then we decompose this copless graph into its connected mini subgraphs. Then we take each
    connected mini subgraph's vertices and induce with them another mini cop subgraph using all the vertices,
    including the cops, of the original graph. A list of these mini cop subgraphs is returned here.

    In the returned list, every subgraph is non-empty and has at least one node that is not a cop.

    @param graph Graph to decompose into mini cop subgraphs
    @return List of graphs that are mini cop subgraphs of the given graph
'''
def decompose_into_connected_components(graph):
    def fresh_node(components, graph):
        for n in graph.nodes():
            if graph.is_cop(n): continue
            inside = False
            for comp in components:
                if n in comp.nodes():
                    inside = True
                    break
            if not inside:
                return n
        return None

    components = []
    first_node = fresh_node(components, graph)
    while first_node is not None:
        worklist = [first_node]
        current_component = Graph()
        while worklist:
            next_node = worklist.pop()
            if next_node in current_component.nodes():
                continue
            neighbours = list(graph.adjacent[next_node])
            is_cop = graph.is_cop(next_node)
            current_component.add(next_node, neighbours, is_cop)
            if is_cop:
                continue
            for neighbour in neighbours:
                worklist.append(neighbour)
        components.append(current_component)
        first_node = fresh_node(components, graph)
    return components

def show_connected_components(graph):
    components = decompose_into_connected_components(graph)
    logging.debug(f'There are {len(components)} connected components in the given graph')
    for i, comp in enumerate(components):
        logging.debug(f'Component #{i+1} is\n{comp}\n')

if __name__ == '__main__':
    # non-trivial graph on 14 vertices
    G = Graph({
        1: [2, 3, 4],
        2: [5, 8],
        3: [7, 8],
        4: [9, 10],
        5: [11, 12],
        6: [13, 14],
        7: [11, 13],
        8: [12, 14],
        9: [11, 14],
        10: [12, 13]
    })

    # trivial forest on 7 vertices
    # G = Graph({
    #     1: [2, 5],
    #     2: [3, 4],
    #     6: [7]
    # })
    G.make_symmetric()
    k = 60

    logging.info(f'We want a tree decomposition of width {k-1} for the following graph:\n{G}')
    search_tree, success = compute_tree_decomposition(G, k)
    if success:
        logging.info('Successfully computed a tree decomposition.')
    else:
        logging.error('Failed computing a tree decomposition.')
        exit(1)

    logging.debug(search_tree.edges_string())
    logging.debug(str(search_tree))
