# Plan for my Master's thesis

## Goal

Write a program that, given a graph and a number p, decomposes the graph into a tree of minimal p-width.
Write this program to be time-efficient, that is, write the program in such a way, that it does not waste its CPU time.

## Steps

0. Download a program that has participated in a previous PACE challenge. Get that program up and running on some of the PACE instances. Per instance, on the one hand, note and visualize the input graph, the found tree decomposition, the tree width and the tree 2-width, and on the other hand, note and visualize some runtime statistics.
The p-width of a tree is the maximum p-width over all bags, where the p-width of a bag is its size, if its degree is smaller than 3, and its size plus p (e.g. p=2), if its degree is at least 3.

1. Implement a simple program that may waste a lot of its CPU time and memory. Do it in Python because in Python, programs are more easily written. Test the simple program on instances downloaded from an earlier PACE challenge. Per instance, note and visualize things as above.

2. Read scientific papers to understand some of the more advanced techniques that are relevant to your task, namely decomposing a graph into interleaving subtrees. You may also study the source code of programs that have been submitted to that previous PACE challenge, aiming to extract some techniques to efficiently rule out ways to decompose a graph.

3. Integrate some of your favourite, understood techniques into your earlier Python program. You may also bluntly copy some of the source code from PACE. Or if a technique is not easily integrated into your earlier program, write a new Python program from scratch using that technique. Test the new program on those PACE instances.

4. If you like a particular set of techniques a lot, translate your respective Python program to Golang, and test it on those PACE instances.

5. Now, using your experience with techniques to minimize tree width, construct your own techniques that, given p, minimize the tree p-width.

6. Implement these techniques in Python. Test them.

7. If it worked well, translate the Python program to C++ or Golang, or both.
