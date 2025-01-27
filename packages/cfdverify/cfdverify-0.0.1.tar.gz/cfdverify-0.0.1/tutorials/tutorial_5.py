"""
This script shows how a custom discretization error model can be created with
whatever combination of models is desired for the analysis.
"""
# %%
## Import modules
from cfdverify.discretization import *

# %%
## Create the default custom model
mesh_sizes = [0.00292402, 0.00414913, 0.00573555] # m
pressure_drop = [100, 98, 95] # kPa
max_vel = [8, 8.5, 9.2] # m/s
model = CustomDiscretizationError(mesh_sizes,
                                  {"DP": pressure_drop, "Vel": max_vel})
model.summarize()

# %%
## Specify individual discretization, error, and uncertainty models
# Be careful, it is very easy to create combinations that are inconsistent!
model = CustomDiscretizationError(mesh_sizes,
                                  {"DP": pressure_drop, "Vel": max_vel},
                                  model=FinestValue,
                                  error=RelativeError,
                                  uncertainty=FactorOfSafety)
model.summarize()