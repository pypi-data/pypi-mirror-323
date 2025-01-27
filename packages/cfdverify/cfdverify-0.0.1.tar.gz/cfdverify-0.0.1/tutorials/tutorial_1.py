"""
This script shows how to run a basic solution verification analysis of a CFD
result.
"""
# %%
## Import modules
from cfdverify.discretization import Classic
import cfdverify.utils as utils

# %%
## Define simulation outputs
# Define average mesh sizes from simulation domain volume and cell counts
simulation_volume = 0.1 # m^3
cell_counts = [4_000_000, 1_400_000, 530_000]
mesh_sizes = utils.mesh_size(simulation_volume, cell_counts)

# Define system response
pressure_drop = [100, 98, 95] # kPa

# %%
## Solve for discretization error
# Create discretization model
model = Classic(mesh_sizes, pressure_drop)

# Print a summary of the solution
model.summarize()

# Plot the data
model.plot()
