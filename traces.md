# Notable traces of programs

Sequoia, given the input
```
./src/sequoia -e MaxCardSet -f formulas/longest-cycle.mso -g ../../easy_graphml/contiki_dhcpc_dhcpc_init.graphml -2
```
outputs
size: 8, members: 64, 63, 29, 27, 28, 61, 62, 30
But there is no node or edge with id 64. But there nodes 27,28,29,30 indeed form a cycle. So what does that mean?
