import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass

import pandas as pd
import tools.TetradSearch as search

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

search = search.TetradSearch()

search.use_sem_bic(df, penalty_discount=2) ## switches to using the SEM BIC score with that data and the given params
search.add_to_tier(1, "Frequency", "Attack", "Chord")
search.add_to_tier(2, "Velocity", "Displacement", "Pressure")

## Run the search and return the graph in PCALG format
g = search.run_fges()

## Print the graph
print(g)

