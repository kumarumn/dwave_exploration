# ------ Import necessary packages ----
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dimod import qubo_to_ising,ising_to_qubo
import networkx as nx
import dwave.inspector

# AND - decomposed manually
# Populate h 
h = {'x':1, 'y':1, 'z':-2}

# Populate J
J = {('x','y'):-1, ('x','z'):2, ('y','z'):2}

# ------- Run our QUBO on the QPU -------
# Set up QPU parameters, change if problem inspector shows a warning
chainstrength = 8
# Set number of samples
numruns = 1000

# Convert the problem from Ising formulation to QUBO
Q,offset0 = ising_to_qubo(h,J)

# Run the QUBO on the solver from your config file
sampler = EmbeddingComposite(DWaveSampler())
#response_ising = sampler.sample_ising(h,J,
#                               chain_strength=chainstrength,
#                               num_reads=numruns,
#                               label='AND Example - ISING')
response = sampler.sample_qubo(Q,
                               chain_strength=chainstrength,
                               num_reads=numruns,
                               label='AND Example - QUBO')

# Dump results to a file
f = open('and.txt','w')
print(response.variables, file=f)
print(response.record, file=f)
f.close()
# Invoke the problem inspector
dwave.inspector.show(response)