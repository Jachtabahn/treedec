!#/bin/bash

dot -Tsvg dot/bag1.dot -o svg/bag1.svg
dot -Tsvg dot/edge2.dot -o svg/edge2.svg
dot -Tsvg dot/edge3.dot -o svg/edge3.svg

dot -Tsvg dot/forest.dot -o svg/forest.svg
