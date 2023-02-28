import os
import sys

# this needs to happen before import pytetrad (otherwise lib cant be found)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from pytetrad.util import startJVM
startJVM()

import pandas as pd
import numpy as np
import pytetrad.translate as tr

import java.util as util
import edu.cmu.tetrad.search as ts

from causallearn.search.ConstraintBased.FCI import fci
from causallearn.utils.cit import chisq, fisherz, kci, d_separation



df = pd.read_csv(f"{BASE_DIR}/examples/resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

data = tr.data_frame_to_tetrad_data(df)
print(data)

variables = data.getVariables()

# score = ts.SemBicScore(data)
# score.setPenaltyDiscount(2)
# score.setStructurePrior(0)

test = ts.IndTestFisherZ(data, 0.05)

print("\nCL FCI\n")
G, edges = fci(np.array(df), fisherz, 0.05)
out = str(G)
for i, col in enumerate(df.columns):
    out = out.replace(f"X{i+1}", col)
print(out)

print("\nTetrad FCI\n")
tetrad_fci = ts.Fci(test)
tetrad_fci_graph = tetrad_fci.search()
print(tetrad_fci_graph)



