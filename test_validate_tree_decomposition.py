import dec
import tree_decomposition
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    test_pairs = [('forest.gr', 'forest.td')]

    for graph_path, tree_path in test_pairs:
        input_graph = dec.parse_graph(graph_path)
        logging.info(f'The input graph is\n{input_graph}')
        input_graph.make_symmetric()

        tree_decomposition = tree_decomposition.parse_tree_decomposition(tree_path)
        logging.debug(f'The tree decomposition is\n{tree_decomposition}')

        valid = tree_decomposition.validate(input_graph)
        if valid:
            logging.info('The tree decomposition is valid.')
        else:
            logging.error('The tree decomposition is invalid.')
