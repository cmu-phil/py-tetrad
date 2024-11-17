import jpype.imports

import importlib.resources as importlib_resources
jar_path = importlib_resources.files('pytetrad').joinpath('resources','tetrad-current.jar')
jar_path = str(jar_path)
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[jar_path])
    except OSError:
        print("can't load jvm")
        pass

import pandas as pd
import pytetrad.tools.TetradSearch as ts

df = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
df = df.astype({col: "float64" for col in df.columns})

search = ts.TetradSearch(df)

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
print(search.get_string())

search.run_dagma()
print(search.get_string())

search.run_direct_lingam()
print(search.get_string())

## Print all subsets independence facts.
print(search.all_subsets_independence_facts(search.get_java()))