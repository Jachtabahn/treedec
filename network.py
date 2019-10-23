from os import path
import os
import logging

class Graph:

    def __init__(self, adjacent=None, cops=None):
        self.adjacent = adjacent if adjacent is not None else dict()
        self.cops = cops if cops is not None else []
        self.new_cop = None

    def vertices(self):
        return list(self.adjacent.keys())

    def copy(self):
        copied_adjacent = dict()
        for vertex, neighbours in self.adjacent.items():
            copied_adjacent[vertex] = list(neighbours)
        copied = Graph(copied_adjacent, list(self.cops))
        return copied

    def add(self, vertex, neighbours, is_cop):
        assert vertex not in self.adjacent
        self.adjacent[vertex] = neighbours
        if is_cop:
            assert vertex not in self.cops
            self.cops.append(vertex)

    def place(self, n):
        if n not in self.cops:
            self.cops.append(n)
            self.new_cop = n

    def is_cop(self, n):
        return n in self.cops

    def make_symmetric(self):
        for vertex, neighbours in list(self.adjacent.items()):
            for neigh in neighbours:
                if neigh not in self.adjacent:
                    self.adjacent[neigh] = [vertex]
                elif vertex not in self.adjacent[neigh]:
                    self.adjacent[neigh].append(vertex)

    '''
        Constructs a list of edges with only one direction for each edge.
    '''
    def one_directional(self):
        edges = []
        for vertex, neighbours in self.adjacent.items():
            for neigh in neighbours:
                if (neigh, vertex) not in edges:
                    edges.append((vertex, neigh))
        return edges

    def visualize(self):
        dot_string = 'graph {\n'
        dot_string += 'bgcolor=transparent\n'
        dot_string += 'node [style=filled, color=aliceblue]\n'
        for vertex in self.vertices():
            if vertex in self.vertices():
                if vertex == self.new_cop:
                    color = ', color=darkgreen'
                elif vertex in self.cops:
                    color = ', color=gray'
                else:
                    color = ''
                dot_string += f'{vertex} [label="{vertex}"{color}]\n'
            else:
                dot_string += f'{vertex} [label="{vertex}", style=invis]\n'

        for tail, head in self.one_directional():
            if tail not in self.vertices() or head not in self.vertices():
                style = ' [style=invis]'
            else:
                style = ''
            dot_string += f'{tail} -- {head}{style}\n'
        dot_string += '}\n'
        return dot_string

    def __str__(self):
        s = '----------- Graph -----------\n'
        for n, a in self.adjacent.items():
            if not self.is_cop(n):
                s += f'Robber {n}: {a}\n'
            else:
                s += f'Cop    {n}: {a}\n'
        return s

'''
    Decomposes a given graph minus its cop vertices into connected subgraphs, where each subgraph still contains
    those cops that surround it. So we take a graph, remove all the cop vertices and that gives us a copless subgraph.
    Then we decompose this copless graph into its connected mini subgraphs. Then we take each
    connected mini subgraph's vertices and induce with them another mini cop subgraph using all the vertices,
    including the cops, of the original graph. A list of these mini cop subgraphs is returned here.

    In the returned list, every subgraph is non-empty and has at least one vertex that is not a cop.

    @param graph Graph to decompose into mini cop subgraphs
    @return List of graphs that are mini cop subgraphs of the given graph
'''
def decompose_into_connected_components(graph):
    def fresh_node(components, graph):
        for n in graph.vertices():
            if graph.is_cop(n): continue
            inside = False
            for comp in components:
                if n in comp.vertices():
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
            if next_node in current_component.adjacent.keys():
                continue
            neighbours = list(graph.adjacent[next_node])
            inside_neighbours = []
            for neigh in neighbours:
                if neigh in current_component.adjacent.keys():
                    inside_neighbours.append(neigh)

            is_cop = graph.is_cop(next_node)
            current_component.add(next_node, inside_neighbours, is_cop)
            if is_cop:
                continue
            for neighbour in neighbours:
                worklist.append(neighbour)
        current_component.make_symmetric()
        components.append(current_component)
        first_node = fresh_node(components, graph)
    return components

def show_connected_components(graph):
    components = decompose_into_connected_components(graph)
    logging.debug(f'There are {len(components)} connected components in the given graph')
    for i, comp in enumerate(components):
        logging.debug(f'Component #{i+1} is\n{comp}\n')

def parse(file):
    '''
        If file is a file, this function consumes the file, that is, it can only be called once.
        If it is called a second time, the function will continue to read the file,
        where it left off last time, namely at the end and read nothing.
    '''
    graph = None
    for line in file:
        if line[0] == 'c': continue

        if line[-1] == '\n':
            line = line[:-1]
        info = line.split(' ')
        if line[0] == 'p':
            if len(info) < 3:
                logging.error(f'The problem line has too few words!')
                return None
            num_vertices = int(info[2])
            graph = Graph()
            for v in range(num_vertices):
                graph.adjacent[v+1] = []
        else:
            if graph is None:
                logging.error(f'Encountered a non-comment line before the problem line!')
                return None
            tail, head = int(info[0]), int(info[1])
            graph.adjacent[tail].append(head)
    return graph
