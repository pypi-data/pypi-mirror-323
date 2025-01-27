"""
This script shows a variety of the discretization error models which are
defined in this package and how they can be used depending on the results of 
your CFD analysis.
"""
# %%
## Import modules
from cfdverify.discretization import Classic, Average

# %%
## Use the Classic model for data which convergences following a power law
mesh_sizes = [0.00292402, 0.00414913, 0.00573555] # m
pressure_drop = [100, 98, 95] # kPa
model = Classic(mesh_sizes, pressure_drop)
model.summarize()

# %%
## Use the Average model for oscillatory data which isn't showing a trend
mesh_sizes = [0.00292402, 0.00414913, 0.00573555, 0.007, 0.009] # m
pressure_drop = [100, 98, 101, 98.4, 100.5] # kPa
model = Average(mesh_sizes, pressure_drop)
model.summarize()
# %%
