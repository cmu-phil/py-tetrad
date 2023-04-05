import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass

import pandas as pd
import tools.TetradSearch as search

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

search = search.TetradSearch(df)

## Use a SEM BIC score
search.use_sem_bic(penalty_discount=2)

## Set knowledge
search.add_to_tier(0, "Frequency")
search.add_to_tier(0, "Attack")
search.add_to_tier(0, "Chord")
search.add_to_tier(1, "Velocity")
search.add_to_tier(1, "Displacement")
search.add_to_tier(1, "Pressure")

## Run the search
search.run_fges()

## Print the graph
print(search.get_string())