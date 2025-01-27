"""
This script explores the various ways a solution verification object can be 
constructed.
"""
# %%
## Import modules
import pandas as pd
from cfdverify.discretization import Classic

# %%
## Create a model for a single system response quantity
# Acceptable data types are: list, tuple, dict, Numpy array, or Pandas Series
mesh_sizes = [0.00292402, 0.00414913, 0.00573555] # m
pressure_drop = [100, 98, 95] # kPa
model = Classic(mesh_sizes, pressure_drop)
model.summarize()

# If using a dict or Pandas Series with a name attribute, the key will be used
model = Classic({"size": mesh_sizes}, pd.Series(pressure_drop, name="DP"))
model.summarize()

# %%
## Create a model for multiple responses with a dictionary
# Multiple responses from the same CFD simulation
mesh_sizes = [0.00292402, 0.00414913, 0.00573555] # m
pressure_drop = [100, 98, 95] # kPa
max_vel = [8, 8.5, 9.2] # m/s
model = Classic(mesh_sizes, {"DP": pressure_drop, "Vel": max_vel})
model.summarize("Vel")

# All data can be passed in a single dictionary if the discretization sizes are
# labeled with the key "hs" or the key is provided as a second argument
model = Classic({"hs": mesh_sizes, "DP": pressure_drop, "Vel": max_vel})
model.summarize("Vel")

# %%
## Create a model with a Pandas DataFrame for importing csv data
# DataFrames are convenient for data in csv form
data = pd.read_csv("example_data.csv")
model = Classic(data, "Meshes")
model.summarize()