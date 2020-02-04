PATH_TO_SEQUOIA=$1

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/clique.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: clique.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: clique.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/connected.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: connected.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: connected.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/3col2.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: 3col2.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: 3col2.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/d2-dominating-set.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: d2-dominating can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: d2-dominating cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/dominating-set.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: dominating-set can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: dominating-set cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/longest-cycle.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: longest-cycle can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: longest-cycle cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/hamiltonian-cycle.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: hamiltonian-cycle can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: hamiltonian-cycle cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/connected-domset.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: connected-domset can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: connected-domset cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/3col.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: 3col.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: 3col.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/independent-set.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: independent-set can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: independent-set cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/3col-free2.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: 3col-free2 can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: 3col-free2 cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/vertex-cover.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: vertex-cover can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: vertex-cover cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/steiner.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: steiner.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: steiner.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/d3-dominating-set.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: d3-dominating can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: d3-dominating cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/bipartite.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: bipartite.mso can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: bipartite.mso cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi

$PATH_TO_SEQUOIA -2 -e Bool -g /var/www/html/networks/graph/structs/network.graphml -f /home/habimm/treedec/sequoia/formulae/3col-free.mso
if [ $? -eq 0 ]
then
    echo '----------------------------------------------------'
    echo 'RESULT: 3col-free can run on the incidence encoding'
    echo '----------------------------------------------------'
else
    echo '----------------------------------------------------'
    echo 'RESULT: 3col-free cannot run on the incidence encoding'
    echo '----------------------------------------------------'
fi
