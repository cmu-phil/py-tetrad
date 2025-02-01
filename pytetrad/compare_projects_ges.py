## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

import io
import sys
import time

from causallearn.search.ScoreBased.GES import ges

import pytetrad.tools.translate as tr
import pytetrad.tools.simulate as sim

import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.search.score as score
import edu.cmu.tetrad.graph as graph
import java.io as _io
import edu.cmu.tetrad.algcomparison.statistic as stat

# important to not randomized the variable order here so that the variables will correspond.
# (CL uses X1, X2,... in order of columns.)
D, G = sim.simulateContinuous(num_meas=20, avg_deg=4, samp_size=1000, rand_cols=False)

D2 = tr.tetrad_data_to_pandas(D)
D2 = D2.astype({col: "float64" for col in D2.columns})

# run cl ges on the data...
start_time = time.time()
cl_ges_graph = ges(D2.to_numpy())['G']
end_time = time.time()

elapsed_time_cl = end_time - start_time

# capture the text output from cl and re-parse it as a Tetrad graph...
output_capture = io.StringIO()
sys.stdout = output_capture
print(cl_ges_graph)
sys.stdout = sys.__stdout__
captured_output = output_capture.getvalue()
output_capture.close()

cl_ges = graph.GraphSaveLoadUtils.readerToGraphTxt(_io.StringReader(captured_output))

# now print that Tetrad graph object from cl...
print('CL GES graph')
print(cl_ges)

# now run fges on it
start_time = time.time()
_score = score.SemBicScore(D, True)
_score.setPenaltyDiscount(2)
tetrad_fges = ts.Fges(_score)
tet_ges = tetrad_fges.search()
end_time = time.time()
elapsed_time_tet = end_time - start_time

# and print that...
print('Tetrad FGES graph')
print(tet_ges)

# now calculate AP for cl and tetrad ges results vis-a-vis true DAG G.
cl_ges = graph.GraphUtils.replaceNodes(cl_ges, G.getNodes())
tet_ges = graph.GraphUtils.replaceNodes(tet_ges, G.getNodes())

ap_cl = stat.AdjacencyPrecision().getValue(G, cl_ges, D)
ap_tet = stat.AdjacencyPrecision().getValue(G, tet_ges, D)

ar_cl = stat.AdjacencyRecall().getValue(G, cl_ges, D)
ar_tet = stat.AdjacencyRecall().getValue(G, tet_ges, D)

ahp_cl = stat.ArrowheadPrecision().getValue(G, cl_ges, D)
ahp_tet = stat.ArrowheadPrecision().getValue(G, tet_ges, D)

ahr_cl = stat.ArrowheadRecall().getValue(G, cl_ges, D)
ahr_tet = stat.ArrowheadRecall().getValue(G, tet_ges, D)

print(f"AP (CL) = {ap_cl:.4f} AP (Tet) {ap_tet:.4f}")
print(f"AR (CL) = {ar_cl:.4f} AP (Tet) {ar_tet:.4f}")
print(f"AHP (CL) = {ahp_cl:.4f} AP (Tet) {ahp_tet:.4f}")
print(f"AHR (CL) = {ahr_cl:.4f} AP (Tet) {ahr_tet:.4f}")
print(f"elapsed (CL) = {elapsed_time_cl:.4f} s, elapsed (Tetrad) = {elapsed_time_tet:.4} s")