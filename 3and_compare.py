# Import networkx for graph
import networkx as nx
# Import pyplot if you want to plot your graph manually
# Problem inspector does a better job at it
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

############## ckt reference ####################
circuit = nx.DiGraph()
circuit.add_node('in1',weight=0)
circuit.add_node('in2',weight=0)
circuit.add_node('in3',weight=0)
circuit.add_node('a')
circuit.add_node('b')
circuit.add_edge('in1','a')
circuit.add_edge('in2','a')
circuit.add_edge('a','b')
circuit.add_edge('in3','b')
port_info = {'in1': 'input', 'in2': 'input', 'in3': 'input', 'a': 'none' ,'b':'output'}
nx.set_node_attributes(circuit,port_info,name='port')
gate_info = {'in1': 'none', 'in2': 'none', 'in3': 'none', 'a': 'and' ,'b':'and'}
nx.set_node_attributes(circuit,gate_info,name='gate')
#################################################

############## ckt implementation ###############
circuit2 = nx.DiGraph()
circuit2.add_node('in1',weight=0)
circuit2.add_node('in2',weight=0)
circuit2.add_node('in3',weight=0)
circuit2.add_node('a')
circuit2.add_node('b')
circuit2.add_edge('in1','a')
circuit2.add_edge('in2','a')
circuit2.add_edge('a','b')
circuit2.add_edge('in3','b')
port_info2 = {'in1': 'input', 'in2': 'input', 'in3': 'input', 'a': 'none' ,'b':'output'}
nx.set_node_attributes(circuit2,port_info2,name='port')
gate_info2 = {'in1': 'none', 'in2': 'none', 'in3': 'none', 'a': 'nand' ,'b':'and'}
nx.set_node_attributes(circuit2,gate_info2,name='gate')
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
            
            first_inp = fan_in[0][0]
            second_inp = fan_in[1][0]
            
            # replicate fan_in and fan_out of gate on gate_template
            # rename inputs
            G.add_edge(first_inp,node_prefix+'x',weight=-2)
            print("Adding edge ",first_inp,node_prefix+'x')        
            G.add_edge(second_inp,node_prefix+'y',weight=-2)
            print("Adding edge ",second_inp,node_prefix+'y')        
            
            for ed in fan_out:
                G.add_edge(node_prefix+'z',ed[1])
            print("Adding edge ",node_prefix+'z',ed[1]) 

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

######### To create a graph layout manually #####
#mypos=nx.spring_layout(circuit)
#labels = {n: (n + "," + str(circuit.nodes[n]['weight'])) for n in circuit.nodes}
#elabels = nx.get_edge_attributes(circuit,'weight')
#nx.draw(circuit, with_labels=True, font_weight='bold', labels=labels)
#nx.draw_networkx_edge_labels(circuit, pos=mypos, label_pos=0.5, edge_labels=elabels)
#plt.savefig("circuit.png")
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

# Add a final node to the output for control
miter.add_edge('xor_b-z-z', 'F', weight=-2)
miter.nodes['F']['port']='output'

# Initialize dictionaries
h = dict(miter.nodes(data="weight", default=0))
J = dict()

# Populate h and J for miter
for i, j in miter.edges:
    J[(i,j)] = miter[i][j]['weight']

for i in miter.nodes:
    print(i,'---')
    print(miter.nodes[i]['port'])

#Set for XOR output = 1, by making node weight negative
#this causes spin to be positive to reduce energy
h['F']=-10

print(h)
print(J)

# Set up QPU parameters
chainstrength = 8
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

f = open('circuit.txt','w')
print(response.variables, file=f)
print(response.record, file=f)
f.close()
#"""
