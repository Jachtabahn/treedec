# Plan for my Master's thesis

## Network inputs overview
* all networks on one continuous page, which is scrollable like a photo album
* each network is spatially visualized in a special rectangle
* one network per row
* each network has a name
* clicking on a network leads to a new page, that is dedicated to this one network

## Visualize a network's tree decompositions
* each tree decomposition has a list of runtimes, which a new invocation of the indicated algorithm used to compute it
* each tree decomposition has a list of parameters, which were passed to the indicated algorithm in every invocation

## Organize all my data

A. Network structure
* network edges

B. Tree decomposition structure
* list of bagged vertices for every node
* tree edges

1. Network instance
* network name
* name of category of networks ('easy' or 'hard')
* path to the .gr file
* number of vertices
* number of edges

2. Tree decomposition
* network name
* solver name
* additional parameters to the solver
* path to the .td file
* number of nodes
* number of join nodes
* number of edges
* treewidth
* joinwidth
* list of runtimes of above solver to compute this exact tree decomposition

3. Solver
* solver name
* solver title
* path to the working directory of solver
* solver command

## Visualize the workings of my search algorithm

I should be able to see the state from which my algorithm makes a decision like placing a cop and the state, where it gets to after making the decision. For fixed input, I want to see different state components at every time step of the trace. The time steps will not be spatially next to each other, but I can click myself from time step to time step. A state component will be spatial. It will be a clickable, movable, two-dimensional colourful picture, together with a key/value table, which gives additional digital information about this state component (for example the number of cops).

1. Then I will generate these trace visualizations for several inputs.
2. I will look through each trace visualization and try to understand my algorithm: From any spatial state, to which other spatial state will my algorithm go?
3. Find a specific spatial state, from where I know a better move, than the one my algorithm makes.
4. Try to generalize from that better move to a whole better subalgorithm, and write that whole better subalgorithm down in pseudo-code.
5. Modify your actual algorithm to include this new subalgorithm.
