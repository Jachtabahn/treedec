# Plan for my master's thesis

## Goal

Write a computer program that, given a network and a natural number p, computes for this network a **tree decomposition of minimal p-treewidth** (see below for definition of p-treewidth).

The **treewidth** of a tree decomposition is the maximum size of the bag minus one, across all nodes' bags (and -1 if there no nodes).

The **joinwidth** of a tree decomposition is the maximum size of the bag minus one, across all join nodes' bags (and -1 if there no join nodes).

The **p-treewidth** of a tree decomposition is the maximum of its treewidth and its joinwidth plus p.

## Steps

1. Setup four different tree decomposition solvers from Github. These *PACE solvers* must have participated in the PACE 2016 or PACE 2017 tree decomposition challenge. Get them up and running on network instances of the PACE 2016 challenge. Per network, one the one hand, describe and visualize the input network, all the solvers' found tree decompositions, their treewidths and joinwidths, and on the other hand, describe and visualize the solvers' runtime statistics for this instance.

2. Implement a simple Python program, that given a network instance and a treewidth, computes a tree decomposition for this network of at most the given treewidth (or says that such a tree decomposition does not exist). Test the simple program on network instances from the PACE 2016 challenge, using the treewidths computed by the PACE solvers. Per instance, describe and visualize the same things as above.

3. Improve your previous Python program to save more computation, when computing a tree decomposition of given treewidth. Make more intelligent choices when considering, where to place the next cop, or which network component to decompose next. Retest your program on PACE 2016 instances and visualize the new results.

4. Modify your previous Python program to compute a tree decomposition of given p-treewidth, instead of just treewidth. This means: Disallow join nodes, where the bag size + p exceeds the given p-treewidth plus one. And like before: Disallow nodes, where the bag size exceeds the given p-treewidth plus one.

5. Compute the 2-treewidths of all the PACE solvers' tree decompositions of PACE 2016 instances. Then use these 2-treewidths as inputs to your Python program to compute tree decompositions. Retest on PACE 2016 instances and visualize your new results.

6. Register your master's thesis with one of the titles "Tree decompositions: Downsizing the bags of join nodes" or "Tree decompositions: Minimizing the size of join nodes".
