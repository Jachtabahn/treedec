import networkx as nx
import logging

'''
p tw 16 40
1 2
1 11
1 14
1 7
1 9
2 16
2 4
2 5
2 10
11 12
12 14
12 15
13 14
14 16
15 16
3 11
3 13
3 16
3 4
3 9
4 12
4 6
4 7
5 11
5 13
5 15
5 6
6 14
6 8
6 9
7 13
7 15
7 8
8 11
8 16
8 10
9 15
9 10
10 12
10 13
'''

def parse(file):
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
            graph = nx.Graph()
            for v in range(num_vertices):
                graph.add_node(v+1)
        else:
            if graph is None:
                logging.error(f'Encountered a non-comment line before the problem line!')
                return None
            tail, head = int(info[0]), int(info[1])
            graph.add_edge(tail, head)

    print(graph.nodes())
    print(graph.edges())

    return graph

with open('../easy/ClebschGraph.gr') as f:
    graph = parse(f)

nx.write_graphml(graph, 'Clebsch.graphml')
