# Import networkx for graph
import networkx as nx
# Import pyplot if you want to plot your graph manually
# Problem inspector does a better job at i
#import matplotlib.pyplot as plt
# DWAVE solvers and inspector
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dimod import qubo_to_ising,ising_to_qubo
import dwave.inspector
from collections import defaultdict

############## AND template #####################
G_and = nx.Graph()
G_and.add_node('x', weight=-1)
G_and.add_node('y', weight=-1)
G_and.add_node('z', weight=2)
G_and.add_edge('x','y', weight=1)
G_and.add_edge('x','z', weight=-2)
G_and.add_edge('y','z', weight=-2)
for i in G_and.nodes:
    G_and.nodes[i]['port'] = 'none'
#################################################

############## OR template ######################
G_or = nx.Graph()
G_or.add_node('x', weight=1)
G_or.add_node('y', weight=1)
G_or.add_node('z', weight=-2)
G_or.add_edge('x','y', weight=1)
G_or.add_edge('x','z', weight=-2)
G_or.add_edge('y','z', weight=-2)
for i in G_or.nodes:
    G_or.nodes[i]['port'] = 'none'
#################################################

############## NAND template ####################
G_nand = nx.Graph()
G_nand.add_node('x', weight=-1)
G_nand.add_node('y', weight=-1)
G_nand.add_node('z', weight=-2)
G_nand.add_edge('x','y', weight=1)
G_nand.add_edge('x','z', weight=2)
G_nand.add_edge('y','z', weight=2)
for i in G_nand.nodes:
    G_nand.nodes[i]['port'] = 'none'
#################################################

############## XOR template #####################
G_xor = nx.Graph()
G_xor.add_node('x0', weight=-1)
G_xor.add_node('y0', weight=-1)
G_xor.add_node('xY', weight=2)
G_xor.add_node('x1', weight=-1)
G_xor.add_node('y1', weight=-1)
G_xor.add_node('Xy', weight=2)
G_xor.add_node('xY1', weight=1)
G_xor.add_node('Xy1', weight=1)
G_xor.add_node('z', weight=-2)
G_xor.add_node('x', weight=0)
G_xor.add_node('y', weight=0)
G_xor.add_weighted_edges_from([('x0','y0',1), ('x0','xY',-2), ('y0','xY',-2), \
    ('x1','y1',1), ('x1','Xy',-2), ('y1','Xy',-2),  \
    ('Xy1','xY1',1), ('xY1','z',-2), ('Xy1','z',-2),    \
    ('Xy','Xy1',-2), ('xY','xY1',-2),   \
    ('x0','x',-2), ('y0','y',2), ('x1','x',2),\
    ('y1','y',-2)])
for i in G_xor.nodes:
    G_xor.nodes[i]['port'] = 'none'
#################################################

############## c17 reference ####################
circuit = nx.DiGraph()
circuit.add_edge('1','10')
circuit.add_edge('3','10')
circuit.add_edge('3','11')
circuit.add_edge('6','11')
circuit.add_edge('2','16')
circuit.add_edge('11','16')
circuit.add_edge('11','19')
circuit.add_edge('7','19')
circuit.add_edge('10','22')
circuit.add_edge('16','22')
circuit.add_edge('16','23')
circuit.add_edge('19','23')
port_info = {'1': 'input', '2': 'input', '3': 'input', '6': 'input', '7': 'input', '10':'none', '11':'none', \
    '16':'none', '19':'none', '22':'output', '23':'output'}
nx.set_node_attributes(circuit,port_info,name='port')
gate_info = {'1': 'none', '2': 'none', '3': 'none', '6': 'none', '7': 'none', '10':'nand', '11':'nand', \
    '16':'nand', '19':'nand', '22':'nand', '23':'nand'}
nx.set_node_attributes(circuit,gate_info,name='gate')
#################################################

############## c17 implementation ###############
circuit2 = nx.DiGraph()
circuit2.add_edge('1','10')
circuit2.add_edge('3','10')
circuit2.add_edge('3','11')
circuit2.add_edge('6','11')
circuit2.add_edge('2','16')
circuit2.add_edge('11','16')
circuit2.add_edge('11','19')
circuit2.add_edge('7','19')
circuit2.add_edge('10','22')
circuit2.add_edge('16','22')
circuit2.add_edge('16','23')
circuit2.add_edge('19','23')
port_info = {'1': 'input', '2': 'input', '3': 'input', '6': 'input', '7': 'input', '10':'none', '11':'none', \
    '16':'none', '19':'none', '22':'output', '23':'output'}
nx.set_node_attributes(circuit2,port_info,name='port')
gate_info = {'1': 'none', '2': 'none', '3': 'none', '6': 'none', '7': 'none', '10':'nand', '11':'nand', \
    '16':'nand', '19':'nand', '22':'nand', '23':'nand'}
nx.set_node_attributes(circuit2,gate_info,name='gate')
#################################################

#### function to replace gates with templates ###
def template_replacement(G):
    # Get the gate type
    gate_info = nx.get_node_attributes(G, 'gate')
    # For each node if the fan_in is two, it is a gate
    # Inversions and buffers can be removed later
    for nd in G.nodes:
        fan_in = list(G.in_edges(nd))
        fan_out = list(G.out_edges(nd))
        # Take union of the graph and gate template
        if len(fan_in) == 2:
            node_prefix = nd + '-'
            if gate_info[nd]=='and':
                G = nx.union(G, G_and, rename=('',node_prefix))
            elif gate_info[nd]=='nand':
                G = nx.union(G, G_nand, rename=('',node_prefix))
            elif gate_info[nd]=='or':
                G = nx.union(G, G_or, rename=('',node_prefix))
            
            first_inp = fan_in[0][0]
            second_inp = fan_in[1][0]
                        
            # replicate fan_in and fan_out of gate on gate_template
            # rename inputs
            G.add_edge(first_inp,node_prefix+'x',weight=-2)
            #print("Adding edge ",first_inp,node_prefix+'x')        
            G.add_edge(second_inp,node_prefix+'y',weight=-2)
            #print("Adding edge ",second_inp,node_prefix+'y')        
            
            for ed in fan_out:
                G.add_edge(node_prefix+'z',ed[1])
                #print("Adding edge ",node_prefix+'z',ed[1]) 

            # rename output
            if G.nodes[nd]['port']=='output':
                G.nodes[node_prefix+'z']['port']='output'   
            
            # remove original gate, keep template
            G.remove_node(nd)

        else:
            print("Node", nd, "is not a two input gate.")
    return G

######## call the function over circuits ########
circuit = template_replacement(circuit)
circuit2 = template_replacement(circuit2)

#print(circuit.nodes)
#print(circuit.edges)
#################################################

# Do not need a directed graph anymore
circuit = circuit.to_undirected()
circuit2 = circuit2.to_undirected()
# Build the miter circuit
miter = nx.union(circuit, circuit2, rename=('r-','i-'))

# Assumes reference and implementation have identical portnames
for i in list(miter.nodes):
    k = str(i)
    # Connect input to primary ones
    if k[0:2]=='r-' and miter.nodes[k]['port']=='input':
        miter.nodes[k]['port']='none'
        miter.add_edge(k[2:],'r-'+k[2:], weight=-2)
        miter.add_edge(k[2:],'i-'+k[2:], weight=-2)
        miter.nodes[k[2:]]['port']='input'
    # Connect outputs to XOR gates
    elif k[0:2]=='r-' and miter.nodes[k]['port']=='output':
        #Add XOR gate between outputs of same name, remove port info
        miter = nx.union(miter, G_xor, rename=('','xor_'+k[2:]+'-'))
        miter.nodes[k]['port']='none'
        miter.add_edge('r-'+k[2:], 'xor_'+k[2:]+'-x', weight=-2)
        miter.add_edge('i-'+k[2:], 'xor_'+k[2:]+'-y', weight=-2)

# Add the final OR gate for the XOR of outputs ##
miter = nx.union(miter, G_or, rename=('','or_22_23-'))
miter.add_edge('xor_23-z-z','or_22_23-x',weight=-2)
miter.add_edge('xor_22-z-z','or_22_23-y',weight=-2)
miter.add_edge('or_22_23-y', 'F', weight=-2)
miter.nodes['F']['port']='output'

# Initialize dictionaries
h = dict(miter.nodes(data="weight", default=0))
J = dict()

# Populate h and J for miter
for i, j in miter.edges:
    J[(i,j)] = miter[i][j]['weight']

#Set for XOR output = 1, by making node weight negative
#this causes spin to be positive to reduce energy
h['F']=-1

print(h)
print(J)

# Set up QPU parameters
chainstrength = 24
numruns = 1000

# Convert the problem from Ising formulation to QUBO
Q,offset0 = ising_to_qubo(h,J)

#"""
## Run the QUBO on the solver from your config file
sampler = EmbeddingComposite(DWaveSampler())

response = sampler.sample_qubo(Q,
                               chain_strength=chainstrength,
                               num_reads=numruns,
                               label='Miter Example')

# Dump results to a file
f = open('c17.txt','w')
print(response.variables, file=f)
print(response.record, file=f)
f.close()
# Invoke the problem inspector
dwave.inspector.show(response)
#"""
