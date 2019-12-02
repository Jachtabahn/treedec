import sys
import argparse
import logging
import network
import itertools

def generate_structures(treewidth):
    input_network = network.parse(sys.stdin)
    logging.info(f'Initiating search for a tree decomposition of width at most {treewidth} for following network.')
    logging.info(input_network)
    input_network.make_symmetric()

    decompositions = dict()

    vertices = input_network.vertices()
    bagsize = treewidth + 1
    for bag in itertools.combinations(vertices, bagsize):
        next_network = input_network.copy()
        for b in bag:
            next_network.place(b)
        components = network.decompose_into_connected_components(next_network)
        decompositions[bag] = components

    logging.info('Done')
    all_components = []
    for bag in decompositions:
        components = decompositions[bag]
        logging.debug(f'Bag {bag} splits the network into following {len(components)} components.')
        for i, comp in enumerate(components):
            logging.debug(f'Component {i+1}:')
            logging.debug(comp)
            all_components.append(comp)

    all_components.sort(key=lambda comp: len(comp.adjacent))
    logging.info(f'There are {len(all_components)} components')
    logging.info(f'First:\n{all_components[0]}')
    logging.info(f'First\'s bag:\n{all_components[0].cops}')
    logging.info(f'Last:\n{all_components[-1]}')

    answers = {}
    for comp in all_components:
        num_vertices = len(comp.adjacent)
        bag = comp.cops
        if num_vertices <= bagsize:
            answers[comp] = True
            continue

        for v in comp.adjacent:
            logging.debug(f'Vertex {v}')
            considering = list(bag) + [v]
            logging.debug(f'Finding vertex separators in {bag+[v]}')

            for w in considering:
                leftout = list(considering)
                leftout.remove(w)

                container = list(comp.adjacent)
                for b in bag:
                    container.remove(b)
                for l in leftout:
                    container.append(l)
                logging.debug(f'Container: {container}')

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--treewidth', '-t', type=int, required=True)
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

    success = generate_structures(args.treewidth)

    if not success:
        logging.error('Failed computing a tree decomposition.')
        exit(1)
