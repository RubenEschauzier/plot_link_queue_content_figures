import numpy as np
import matplotlib.pyplot as plt
import json
import operator
import pandas as pd
# Opening JSON file
f = open('timing_all_combinations.json')

# returns JSON object as
# a dictionary
experiment_data = json.load(f)

priority_orders = [x['priorityOrder'] for x in experiment_data]
dieffAtComplete = np.array([x['dieffAtComplete'] for x in experiment_data], dtype=float)
meanTotalExecutionTime = [x['meanTotalExecutionTime'] for x in experiment_data]
stdTotalExecutionTime = [x['stdTotalExecutionTime'] for x in experiment_data]
meanArrivalTimes = [x['meanArrivalTimes'] for x in experiment_data]
stdArrivalTimes = [x['stdArrivalTimes'] for x in experiment_data]
meanFirstArrivalTimes = [x['meanArrivalTimes'][0] for x in experiment_data]
stdFirstArrivalTimes = [x['stdArrivalTimes'][0] for x in experiment_data]

# _ = plt.hist(meanFirstArrivalTimes, bins='auto')  # arguments are passed to np.histogram
# plt.title("Histogram with 'auto' bins")
# plt.show()
#
# _ = plt.hist(dieffAtComplete, bins='auto')  # arguments are passed to np.histogram
# plt.title("Histogram with 'auto' bins")
# plt.show()

from scipy import stats

res = stats.normaltest(np.array(dieffAtComplete), nan_policy='omit')

print(res)
_ = plt.hist(meanTotalExecutionTime, bins='auto')  # arguments are passed to np.histogram
plt.title("Histogram with 'auto' bins")
plt.show()

df_priorities = pd.DataFrame(priority_orders, columns=['type','contains','storage', 'cMatch',
                                                       'seeAlso', 'sameAs', 'isTopicOf'])
test = pd.get_dummies(df_priorities.astype(str))
print(test)


min_index_total, min_value_total = min(enumerate(meanTotalExecutionTime), key=operator.itemgetter(1))
max_index_total, max_value_total = max(enumerate(meanTotalExecutionTime), key=operator.itemgetter(1))
min_index_dieff, min_value_dieff = min(enumerate(dieffAtComplete), key=operator.itemgetter(1))
max_index_dieff, max_value_dieff = max(enumerate(dieffAtComplete), key=operator.itemgetter(1))
min_index_f_a, min_val_f_a = min(enumerate(meanFirstArrivalTimes), key=operator.itemgetter(1))
max_index_f_a, max_val_f_a = max(enumerate(meanFirstArrivalTimes), key=operator.itemgetter(1))

print("Max & min dieff")
print(max(dieffAtComplete), priority_orders[max_index_dieff])
print(min(dieffAtComplete), priority_orders[min_index_dieff])
print("Max & Min First result arrival time")
print(max_val_f_a, stdFirstArrivalTimes[max_index_f_a], priority_orders[max_index_f_a])
print(min_val_f_a, stdFirstArrivalTimes[min_index_f_a], priority_orders[min_index_f_a])
print("Max & Min mean total execution time")
print(max_value_total, stdTotalExecutionTime[max_index_total])
print(min_value_total, stdTotalExecutionTime[min_index_total])
# Closing file
f.close()
