
## Tree decompositions

Let `G` be a graph. This graph can lose a set `B` of vertices. The graph `G \ B` may be disconnected. It is searched the best way to decompose the graph in this way.

Let C be a component of G \ B.

Let k be a number.
Let G be a connected graph and B a subset of V(G) with |B| <= k+1. Let b = k + 1 - |B|. Now add vertices to B until B has exactly k + 1 vertices.

Look at G \ B. Now take some component C of G \ B. Let D the subset of B of all vertices, which are adjacent to some vertex in C. Set G = C and B = D, and repeat.



Now, choose another subset A of V(G) with at most b vertices. Now, form B = D | A.
