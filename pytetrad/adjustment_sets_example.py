## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad
from email.charset import add_alias

import pandas as pd
import pytetrad.tools.TetradSearch as ts
import pytetrad.tools.simulate as sim
import pytetrad.tools.translate as tr

D, G = sim.simulateContinuous(num_meas=10, avg_deg=4, samp_size=1000)
data = tr.tetrad_data_to_pandas(D)
data = data.astype({col: "float64" for col in data.columns})

search = ts.TetradSearch(data)
search.use_sem_bic()
search.run_boss()
graph = search.get_java()
print(graph)

nodes = graph.getNodes()

max_num_sets=10
max_distance_from_point=5
near_which_endpoint=3
max_path_length=20

for i in range(0, nodes.size()):
    for j in range(0, nodes.size()):
        try:
            adj_sets = search.get_adjustment_sets(graph, nodes.get(i), nodes.get(j),
                                                  max_num_sets=max_num_sets,
                                                  max_distance_from_point=max_distance_from_point,
                                                  near_which_endpoint=near_which_endpoint,
                                                  max_path_length=max_path_length)
            print(f"Adjustment sets for source = {nodes.get(i).getName()} target = {nodes.get(j).getName()}")

            for adj_set in adj_sets:
                print(adj_set)

            print()
        except Exception:

            # Either there are no amenable paths or source == target.
            pass


