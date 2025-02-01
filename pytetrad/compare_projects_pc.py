## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import pandas as pd
import numpy as np
import pytetrad.tools.translate as tr

import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.test as test

try:
    from causallearn.search.ConstraintBased.PC import pc
    from causallearn.utils.cit import fisherz
except ImportError as e:
    print('Could not import a causal-learn module: ', e)

df = pd.read_csv(f"resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.pandas_data_to_tetrad(df)

print("\nCL PC\n")
cg = pc(np.array(df), 0.05, fisherz, node_names=df.columns)
print(cg.G)

print("\nTetrad PC\n")
test = test.IndTestFisherZ(data, 0.05)
tetrad_pc = ts.Pc(test)
tetrad_pc_graph = tetrad_pc.search()

print(tetrad_pc_graph)

## PRINTOUT:

# CL PC
#
# Depth=3, working on node 5: 100%|██████████| 6/6 [00:00<00:00, 1342.61it/s]
# Graph Nodes:
# Frequency;Attack;Chord;Velocity;Displacement;Pressure
#
# Graph Edges:
# 1. Frequency --> Attack
# 2. Frequency --- Velocity
# 3. Frequency --> Pressure
# 4. Chord --> Attack
# 5. Velocity --> Attack
# 6. Displacement --> Attack
# 7. Chord --- Displacement
# 8. Chord --> Pressure
# 9. Velocity --> Pressure
# 10. Displacement --> Pressure
#
#
# Tetrad PC
#
# new thread
# Graph Nodes:
# Frequency;Attack;Chord;Velocity;Displacement;Pressure
#
# Graph Edges:
# 1. Attack --> Chord
# 2. Chord --> Pressure
# 3. Displacement --> Attack
# 4. Displacement --> Chord
# 5. Displacement --> Pressure
# 6. Frequency --> Attack
# 7. Frequency --> Pressure
# 8. Frequency --- Velocity
# 9. Velocity --> Attack
# 10. Velocity --> Pressure
