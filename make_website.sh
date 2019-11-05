
echo "Preparing the visualization folders.."
python ~/treedec/habimm/prepare.py \
    -s ~/treedec/visualization/networks \
    -n ~/treedec/easy \
    -o "Easy"
echo "Prepared the visualization folders."

echo "Running all the solvers.."
python ~/treedec/habimm/run.py \
    -n ~/treedec/visualization/networks/ \
    -s ~/treedec/habimm/solvers2.json \
    -v
echo "All solvers finished."

echo "Visualizing all structures.."
python ~/treedec/habimm/visual.py \
    -d ~/treedec/visualization/networks
echo "All structures visualized."
