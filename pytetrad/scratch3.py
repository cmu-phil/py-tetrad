import jpype.imports
from torch.ao.quantization.fx import convert

try:
    jpype.startJVM(classpath=[f"resources/tetrad-current.jar"])
except OSError:
    print("JVM already started")

import numpy as np

import edu.cmu.tetrad.graph as tgraph
import edu.cmu.tetrad.sem as tsem
import edu.cmu.tetrad.search as tsearch

import tools.TetradSearch as ts
import tools.translate as tr

# Convert a Java double[][] matrix to a numpy array
def convert_matrix(matrix):
    return np.array([[matrix[i][j] for j in range(matrix[i].length)] for i in range(matrix.length)])

graph = tgraph.RandomGraph.randomGraph(10, 0, 10, 10, 10, 10, True)
sem_pm = tsem.SemPm(graph)
sem_im = tsem.SemIm(sem_pm)
data = sem_im.simulateData(1000, False)
edge_coef = sem_im.getEdgeCoef().toArray()

print("Edge coef")
print(np.array(edge_coef))

df = tr.tetrad_data_to_pandas(data)
df = df.astype({col: "float64" for col in df.columns})

search = ts.TetradSearch(df)
search.use_sem_bic()
search.run_boss()
cpdag = search.get_java()

print("CPDAG")
print(cpdag)

## We have a choice of distance type

# dist_type = tsearch.CpdagParentDistancesFromTrue.DistanceType.SQUARED
dist_type = tsearch.CpdagParentDistancesFromTrue.DistanceType.ABSOLUTE

cpdag_distances = tsearch.CpdagParentDistancesFromTrue()
distances_ = cpdag_distances.getDistances(cpdag, edge_coef, data, dist_type)
minCoef_ = cpdag_distances.getMinCoef()
maxCoef_ = cpdag_distances.getMaxCoef()

# Convert Java double[][] arrays to numpy arrays
distances = convert_matrix(distances_)
minCoef = convert_matrix(minCoef_)
maxCoef = convert_matrix(maxCoef_)


print("Distances")
print(distances)

print("Min coef")
print(minCoef)

print("Max coef")
print(maxCoef)