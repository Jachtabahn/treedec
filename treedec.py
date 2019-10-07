import logging

def intersect(first, second):
    for a in first:
        if a in second:
            return a
    return None

def convert_to_ints(l):
    for i in range(len(l)):
        l[i] = int(l[i])

class TreeDecomposition:

    def __init__(self, bag, tree_id, children):
        self.bag = bag
        self.id = tree_id
        self.children = children

    def extract_bags(self, vertex):
        if vertex in self.bag:
            vertex_bags = [self.id]
            for child in self.children:
                extracted_bags = child.extract_bags(vertex)

                # check if there is some disconnectedness somewhere down below the tree
                if extracted_bags is None: return None

                # check if the vertex re-appears further below in the tree
                if len(extracted_bags) == 0: continue

                # if the vertex does re-appear, then, to be connected, it must be here, too
                if vertex not in child.bag: return None

                vertex_bags += extracted_bags
        else:
            vertex_bags = []
            for child in self.children:
                extracted_bags = child.extract_bags(vertex)
                if extracted_bags is None: return None
                if len(extracted_bags) == 0: continue
                if len(vertex_bags) > 0: return None
                vertex_bags = extracted_bags
        return vertex_bags

    def validate(self, graph):
        bags_per_vertex = dict()
        for vertex in graph.adjacent:
            # try to compute the subtree of all the bags containing the vertex
            vertex_bags = self.extract_bags(vertex)
            if vertex_bags == []:
                logging.error(f'Vertex {vertex} has no bags')
                return False
            if vertex_bags is None:
                logging.error(f'Vertex {vertex} has two unconnected bags')
                return False

            bags_per_vertex[vertex] = vertex_bags

        # check that all edges are bagged
        for vertex, neigh in graph.one_directional():
            vertex_bags = bags_per_vertex[vertex]
            neigh_bags = bags_per_vertex[neigh]

            shared_bag = intersect(vertex_bags, neigh_bags)
            if shared_bag is not None:
                logging.debug(f'The edge between vertices {vertex} and {neigh} is covered by the bag {shared_bag}')
            else:
                logging.error(f'The edge between vertices {vertex} and {neigh} is not covered')
                logging.debug(f'The ids of the first vertex are {vertex_bags} and those of the second are {neigh_bags}')
                return False
        return True

    def td_format(self, bag_id=1):
        bags_string = f'b {bag_id}'
        for vertex in self.bag:
            bags_string += f' {vertex}'
        bags_string += '\n'

        num_bags = 1
        maximum_bag_size = len(self.bag)
        vertices = set(self.bag)
        edges_string = ''
        for i, child in enumerate(self.children):
            child_id = bag_id + num_bags
            child_num_bags, child_maximum_bag_size, child_vertices, \
                child_edges_string, child_string = child.td_format(child_id)

            num_bags += child_num_bags
            maximum_bag_size = max(maximum_bag_size, child_maximum_bag_size)
            vertices = vertices.union(child_vertices)
            edges_string += f'{bag_id} {child_id}\n{child_edges_string}'
            bags_string += child_string
        return num_bags, maximum_bag_size, vertices, edges_string, bags_string

    def save(self, file):
        num_bags, maximum_bag_size, vertices, edges_string, bags_string = self.td_format()
        treedec_string = f's td {num_bags} {maximum_bag_size} {len(vertices)}\n'
        treedec_string += bags_string
        treedec_string += edges_string
        file.write(treedec_string)

    def spaced_string(self, spaces=0):
        s = ''
        s += f'Bag {self.id} contains the vertices {self.bag}\n'
        for child in self.children:
            s += ' '*spaces + child.spaced_string(spaces+1)
        return s

    def __str__(self):
        return self.spaced_string()

def get_children(tree_id, parents, edges):
    children_ids = []
    for edge in edges:
        if tree_id == edge[0] and edge[1] not in parents:
            children_ids.append(edge[1])
        if tree_id == edge[1] and edge[0] not in parents:
            children_ids.append(edge[0])
    return children_ids

def fill_up(trees, bag_id, parents, edges):
    children_ids = get_children(bag_id, parents, edges)
    child_parents = parents[:] + [bag_id]
    for child_id in children_ids:
        trees[bag_id-1].children.append(trees[child_id-1])
        fill_up(trees, child_id, child_parents, edges)

def parse_tree_decomposition(filepath):
    index, edges, trees = 1, [], []
    file = open(filepath, 'r')
    for line in file:
        info = line[:-1].split(' ')
        if info[0] == 'c': continue
        if info[0] == 's': continue
        if info[0] == 'b':
            bag_content = info[1:]
            convert_to_ints(bag_content)
            tree_decomposition = TreeDecomposition(bag_content, index, [])
            index += 1
            trees.append(tree_decomposition)
            continue
        convert_to_ints(info)
        edges.append(info)
    file.close()

    fill_up(trees, 1, [], edges)
    return trees[0]

def extract_bag_size(treedec_path):
    file = open(treedec_path, 'r')
    for line in file:
        info = line[:-1].split(' ')
        if info[0] == 'c': continue
        if info[0] == 's':
            maximum_bag_size = int(info[3])
            return maximum_bag_size
    file.close()
    return None
