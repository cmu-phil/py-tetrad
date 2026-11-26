## This script assumes that the user has pip-installed the pytetrad package. Here is how:
## pip install git+https://github.com/cmu-phil/py-tetrad

# BOSS Top-K keeps the best few models BOSS comes across, not only the best one. This shows how to run it and how
# to get at the models it kept. It needs a tetrad-current.jar built from development on or after 2026-11-26.
import pandas as pd

import pytetrad.tools.TetradSearch as ts

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

search = ts.TetradSearch(data)
search.use_sem_bic(penalty_discount=2)

## With split_delta=0 and one start this is plain BOSS, and one model is kept. A split_delta above 0 sets aside
## every placement of a variable that scores within that much of the best one, and searches from it later.
search.run_boss_topk(top_k=5, split_delta=5.0, max_runs=500)

## The best graph is the result, as for any other search.
print("Best graph:")
print(search.get_string())

## The models kept, best first. The first is the best graph above.
graphs = search.get_topk_graphs()
scores = search.get_topk_scores()
orders = search.get_topk_orders()

print(f"Models kept: {len(graphs)}")

for i, (graph, score, order) in enumerate(zip(graphs, scores, orders)):
    print(f"\nModel {i + 1}: score {score:.3f}, {score - scores[0]:.3f} from the best")
    print("Order: " + ", ".join(order))
    print(search.get_string(graph))
