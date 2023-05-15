import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

import pandas as pd

import tools.TetradSearch as search

data = pd.read_csv("resources/airfoil-self-noise.continuous.txt", sep="\t")
data = data.astype({col: "float64" for col in data.columns})

## Make a TetradSearch instance to run searches against. This helps to organize
## the use of Tetrad search algorithms and hides the JPype code for those who
## don't want to deal with it.
search = search.TetradSearch(data)
search.set_verbose(False)

## Pick the score to use, in this case a continuous linear, Gaussian score.
search.use_sem_bic()
search.use_fisher_z(alpha=0.05)

## Run various algorithms and print their results. For now (for compability with R)
print('FGES')
search.run_fges()
print(search.get_pcalg())

print('BOSS')
search.run_boss()
print(search.get_string())

print('SP')
search.run_sp()
print(search.get_string())

print('GRaSP')
search.run_grasp()
print(search.get_string())

print('PC')
search.run_pc()
print(search.get_string())

print('FCI')
search.run_fci()
print(search.get_string())

print('GFCI')
search.run_gfci()
print(search.get_string())

print('BFCI')
search.run_bfci()
print(search.get_string())

print('GRaSP-FCI')
search.run_grasp_fci()
print(search.get_string())

print('CCD')
search.run_ccd()
print(search.get_string())

print('SVAR-GFCI')
search.run_svar_gfci()
print(search.get_string())

print('SP-FCI')
search.run_spfci()
print(search.get_string())

print('ICA-LiNGAM')
search.run_ica_lingam(threshold_b=0.4, threshold_spine=0)
print(search.get_string())

print('ICA-LiNG-D')
search.run_ica_lingd(threshold_b=0.4, threshold_spine=0)
print(search.get_string())
