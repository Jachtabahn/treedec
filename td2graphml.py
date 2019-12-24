import sys
import argparse
import logging

file_prefix = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="bag" for="node" attr.name="sequoia_bag" attr.type="string" />
  <graph id="G" edgedefault="directed" parse.nodeids="canonical" parse.edgeids="canonical" parse.order="nodesfirst">
'''

file_suffix = '''  </graph>
</graphml>
'''

bag_definition = '''    <node id="{}">
      <data key="bag">{}</data>
    </node>
'''

edge_definition = '''    <edge source="{}" target="{}" />
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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

    sys.stdout.write(file_prefix)
    for line in sys.stdin:
        info = line.split()
        if info[0] == 'c': continue
        if info[0] == 's': continue
        if info[0] == 'b':
            bag_index = info[1]
            decreased_vertices = [str(int(vertex)-1) for vertex in info[2:]]
            bag_content = ' '.join(decreased_vertices)
            my_bag_definition = bag_definition.format(bag_index, bag_content)
            sys.stdout.write(my_bag_definition)
        else:
            source = info[0]
            target = info[1]
            my_edge_definition = edge_definition.format(source, target)
            sys.stdout.write(my_edge_definition)
    sys.stdout.write(file_suffix)
