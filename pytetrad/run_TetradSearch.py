import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass

import pandas as pd
import tools as search
search = search.TetradSearch()

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

## Use a SEM BIC score
search.use_sem_bic(df, penalty_discount=2)

## Set knowledge
search.add_to_tier(1, "Frequency")
search.add_to_tier(1, "Attack")
search.add_to_tier(1, "Chord")
search.add_to_tier(2, "Velocity")
search.add_to_tier(2, "Displacement")
search.add_to_tier(2, "Pressure")

## Run the search
search.run_fges()

## Print the graph
print(search.get_string())

