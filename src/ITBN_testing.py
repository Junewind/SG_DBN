from pgmpy.models import IntervalTemporalBayesianNetwork
from pgmpy.estimators import HillClimbSearchITBN, BicScore
import pandas as pd
import numpy as np
import networkx as nx
import os

# Generate randomized input data
num_samples = 500
num_events = 4
raw = np.random.randint(0, 1, size=(num_samples * 1.25, 3 * num_events))
# Command: starts 0-3, lasts 1-3
raw[0:num_samples, 0] = np.random.randint(0, 4, size=num_samples)
raw[0:num_samples, 1] = raw[0:num_samples, 0] + np.random.randint(1, 4, size=num_samples)
raw[0:num_samples, 2] = 1
# Wave: starts 2-5 after command ends, lasts 1-4
raw[0:num_samples, 3] = raw[0:num_samples, 1] + np.random.randint(2, 6, size=num_samples)
raw[0:num_samples, 4] = raw[0:num_samples, 3] + np.random.randint(1, 5, size=num_samples)
raw[0:num_samples, 5] = np.random.randint(0, 2, size=num_samples)
# Abort: starts 5-7 after command ends, lasts 1-3
raw[0:num_samples, 6] = raw[0:num_samples, 1] + np.random.randint(5, 8, size=num_samples)
raw[0:num_samples, 7] = raw[0:num_samples, 6] + np.random.randint(1, 4, size=num_samples)
raw[0:num_samples, 8] = 0
# Reward: starts 3-5 after wave ends, lasts 2-4
raw[0:num_samples, 9] = raw[0:num_samples, 4] + np.random.randint(3, 6, size=num_samples)
raw[0:num_samples, 10] = raw[0:num_samples, 9] + np.random.randint(2, 5, size=num_samples)
raw[0:num_samples, 11] = 0
# Adjust time for simulated empty videos
raw[num_samples:, 0] = -1
raw[num_samples:, 3] = -1
raw[num_samples:, 6] = -1
raw[num_samples:, 9] = -1
# Adjust conditional events
for row in raw[0:num_samples]:
    if row[5] == 1:
        row[11] = 1
        row[6] = -1
    else:
        row[8] = 1
        row[3] = -1
        row[9] = -1

# Create dataframes
data = pd.DataFrame(raw, columns=['Command_s', 'Command_e', 'Command',
                                  'Wave_s', 'Wave_e', 'Wave',
                                  'Abort_s', 'Abort_e', 'Abort',
                                  'Reward_s', 'Reward_e', 'Reward'])
state_data = data[['Command', 'Wave', 'Abort', 'Reward']]

# Create empty model and add event nodes
model = IntervalTemporalBayesianNetwork()
model.add_nodes_from(state_data.columns.values)

# Learn temporal relations from data
model.learn_temporal_relationships(data)

# Learn model structure from data and temporal relations
hc = HillClimbSearchITBN(state_data, scoring_method=BicScore(state_data))
model = hc.estimate(start=model)
model.add_temporal_nodes()

# Learn model parameters
# model.fit(list(data[model.nodes()]))
for cpd in model.get_cpds():
    print(cpd)

# Draws and outputs resulting network
model.draw_to_file("../output/itbn.png")
os.system('gnome-open ../output/itbn.png')
nx.write_gpickle(model, "../output/itbn.nx")
