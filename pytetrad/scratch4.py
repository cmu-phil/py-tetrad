import pytetrad.tools.simulate as sim
import pytetrad.tools.translate as tr
import pytetrad.tools.TetradSearch as tets

# Load the airfoil data
D, G = sim.simulateContinuous(num_meas=20, samp_size=100, avg_deg=4)

df = tr.tetrad_data_to_pandas(D)

print(df)


print(df.dtypes)

df = df.astype({col: "float64" for col in df.columns})


print(df)

# Do a search on the dataset
ts = tets.TetradSearch(df)
ts.use_sem_bic()
ts.run_fges()
G2 = ts.get_java()

print(G2)


