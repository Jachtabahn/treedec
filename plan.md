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



Take the sequoia-mso solver, look at it and and get it to run on some graph and mso formula
	1. Input into the sequoia solver different graphs and mso formulas,
	2. note the runtimes of the solver

Meiji 2016 tree decomposition
	1. Input into the sequoia solver the same graphs and formulas and Meiji 2016 tree decompositions of those graphs
	2. note the runtimes of the solver

Habimm tree decompositions
	1. Input into the sequoia solver the same graphs and formulas and my own tree decompositions of those graphs
	2. note the runtimes of the solver


Visualize the workings of my search algorithm: I should be able to see the state from which my algorithm makes a decision like placing a cop and the state where it gets to after making the decision. For fixed input, I want to see different state components at every time step of the trace. The time steps will not spatially next to each other, but I can click myself from time step to time step. A state component will be spatial. It will be a clickable, movable, two-dimensional colourful picture, together with a key/value table which gives additional digital information about this state component (for example the number of cops).

1. Then I will generate these trace visualizations for several inputs.
2. I will look through each trace visualization and try to understand my algorithm: From any spatial state, to which other spatial state will my algorithm go?
3. Find a specific spatial state, from where I know a better move than the one my algorithm makes.
4. Try to generalize from that better move to a whole subalgorithm, and write it down in pseudo-code.
5. Actually modify your algorithm to include this new subalgorithm.
