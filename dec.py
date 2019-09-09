

class Graph:

    def __init__(self, adjacent=None, cops=None):
        self.adjacent = adjacent if adjacent is not None else dict()
        self.cops = cops if cops is not None else []

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

    def is_cop(self, n):
        return n in self.cops

    def __str__(self):
        s = '----------- Graph -----------\n'
        for n, a in self.adjacent.items():
            if not self.is_cop(n):
                s += f'Robber {n}: {a}\n'
            else:
                s += f'Cop    {n}: {a}\n'
        return s

output_ids = 1
class TreeDecomposition:

    def __init__(self, subgraph):
        self.subgraph = subgraph
        self.children = []

        global output_ids
        self.output_id = output_ids
        output_ids += 1

    def add(self, child):
        self.children.append(child)

    def edges_string(self):
        s = f'Bag {self.output_id}: ' + str([child.output_id for child in self.children]) + '\n'
        for child in self.children:
            s += child.edges_string()
        return s

    def __str__(self):
        s = f'Bag {self.output_id} contains the subgraph\n' + str(self.subgraph) + '\n'
        for child in self.children:
            s += str(child)
        return s

def treedec(split_graph, k):
    decomposition = TreeDecomposition(split_graph)

    print(f'The given split graph is\n{split_graph}')

    # want all children of this decomposition
    components = decompose_into_connected_components(split_graph)
    for escape_component in components:
        print(f'The next escape component is\n{escape_component}')

        num_cops = len(escape_component.cops)
        print(f'Its number of cops is {num_cops}')
        if num_cops >= k:
            return None

        # want at least one bag for this component
        child = None
        while child is None:
            next_split_graph = escape_component.copy()
            cop_position = choose_cop(next_split_graph)
            print(f'For that escape component we try setting a cop at {cop_position}')
            next_split_graph.place(cop_position)
            child = treedec(next_split_graph, k)
        print(f'We add a child decomposition with subgraph\n{child.subgraph}')
        decomposition.add(child)

    return decomposition

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

def decompose_into_connected_components(graph):
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

def choose_cop(graph):
    for n in graph.nodes():
        if not graph.is_cop(n):
            return n

def get_neighbours_of_cops(graph):
    neighs = []
    for n, neighbours in graph.adjacent.items():
        if graph.is_cop(n):
            neighs += neighbours
    return neighs

if __name__ == '__main__':
    G = Graph({
        1: [2, 5],
        2: [3, 4],
        3: [2],
        4: [2],
        5: [1],
        6: [7],
        7: [6]
    })
    k = 2
    print(f'We want a tree decomposition of width {k-1} for the following graph:\n{G}')
    treedecomposition = treedec(G, k)
    print('The final tree decomposition is')
    print(f"{treedecomposition.edges_string()}")
    print(f"{treedecomposition}")
