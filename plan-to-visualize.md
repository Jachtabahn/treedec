# How to visualize tree decompositions

## Overview
* all graphs on one continuous page, which is scrollable like a photo album
* each network is spatially visualized in a special rectangle
* one network per row
* each network has a name
* clicking on a network leads to a new page, that is dedicated to this one network

The network page shows the network itself and its tree decompositions.

## Network itself
* name of the network
* number of vertices
* number of edges
* the network itself spatially visualized in a special rectangle
* can drag my view on the network by clicking on empty space
* can scroll my view to and from the network
* can drag vertices around
* each vertex is labelled with its id
* can click on a vertex to highlight this vertex and all its edges

## The network's tree decompositions
* listed row-wise below the network, one tree decomposition per row
* each tree decomposition has a name, which could indicate the used algorithm
* each tree decomposition is spatially visualized in a special rectangle
* can drag my view on the tree decomposition by clicking on empty space
* can scroll my view to and from the tree decomposition
* can drag nodes around
* each node is labelled with its bag content
* can click on a node to highlight this node and all its edges
* each tree decomposition has a treewidth and a joinwidth
* each tree decomposition has a list of runtimes, which a new invocation of the indicated algorithm used to compute it
* each tree decomposition has a list of parameters, which were passed to the indicated algorithm in every invocation

## Generation of a network page

Given a network file, for example ClebschGraph.gr.

1. Generate a directory:
    ClebschGraph/
    ├── index.html
    ├── scalars.json
    ├── visuals/
    └── structs/
        ├── network.gr

The file *scalars.json* will contain basic easily computable information about the network, like the number of nodes, edges, the network's name.

2. Compute tree decompositions using various solvers:
    ClebschGraph/
    ├── index.html
    ├── scalars.json
    ├── visuals/
    └── structs/
        ├── network.gr
        ├── habimm.td
        ├── meiji2016.td
        └── utrecht.td

3. Create dot files from the network file and the various tree decomposition files:
    ClebschGraph/
    ├── index.html
    ├── scalars.json
    ├── visuals/
    │   ├── network.dot
    │   ├── habimm.dot
    │   ├── meiji2016.dot
    │   └── utrecht.dot
    └── structs/
        ├── network.gr
        ├── habimm.td
        ├── meiji2016.td
        └── utrecht.td
