import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

import tools.TetradSearch as search

data = pd.read_csv("resources/auto-mpg.data.mixed.max.3.categories.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns if col != "origin"})

## Make a TetradSearch instance to run searches against. This helps to organize
## the use of Tetrad search algorithms and hides the JPype code for those who
## don't want to deal with it.
search = search.TetradSearch(data)
search.set_verbose(False)

## Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_conditional_gaussian_score()
search.use_conditional_gaussian_test()

## Run various algorithms and print their results. For now (for compability with R)
## all graphs are returned in PCALG general graph format.
## Commenting out the ones that won't work with mixed data.
fges_graph = search.run_fges()
print('FGES')
print(fges_graph)

boss_graph = search.run_boss()
print('BOSS')
print(boss_graph)

sp_graph = search.run_sp()
print('SP')
print(sp_graph)

grasp_graph = search.run_grasp()
print('GRaSP')
print(grasp_graph)

# gango_graph = search.run_gango()
# print('GANGO', gango_graph)

pc_graph = search.run_pc()
print('PC')
print(pc_graph)

fci_graph = search.run_fci()
print('FCI')
print(fci_graph)

gfci_graph = search.run_gfci()
print('GFCI')
print(gfci_graph)

bci_graph = search.run_bfci()
print('BFCI')
print(bci_graph)

graph_fci_graph = search.run_grasp_fci()
print('GRaSP-FCI')
print(graph_fci_graph)

ccd_graph = search.run_ccd()
print('CCD')
print(ccd_graph)

# svar_fci_graph = search.run_svar_fci()
# print('SVAR-FCI')
# print(svar_fci_graph)
