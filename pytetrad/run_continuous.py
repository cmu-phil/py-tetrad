import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass
    # print("JVM already started")

import pandas as pd

import tools.TetradSearch as search

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

search = search.TetradSearch(data)
search.set_verbose(False)

search.use_sem_bic(penalty_discount=2)
search.use_fisher_z(alpha=0.05)

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

gango_graph = search.run_gango()
print('GANGO', gango_graph)

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

svar_fci_graph = search.run_svar_fci()
print('SVAR-FCI')
print(svar_fci_graph)
