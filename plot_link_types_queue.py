import ast
from collections import Counter
import pylab as plt
import numpy as np

# The TypeIndexes actor gets called multiple times during query execution, very often (almost all of the time),
# this is for when there are no type indexes available.

# Discover 7 has tons of type index dereferences / searches

# Plot number of types links in queue
# % of time more than one type of link in queue (metric)

# Which link types contributes most to results of query result
# Decreasing weight for reward score for parents of result link type

# Time on x axis
def load_data(location):
    with open(location) as f:
        data = f.read()
    return ast.literal_eval(data)


def stack_link_type_occurrence_data(list_link_priorities):
    priorities = range(0, 8)  # [0, 1, ..., 6] iterator
    num_priority_data = {p: [] for p in priorities}  # or just {p: [] for p in range(0, 7)}

    for priority_count in list_link_priorities:
        counts = Counter(priority_count)
        for priority_num in priorities:
            if counts.get(priority_num):
                num_priority_data[priority_num].append(counts.get(priority_num))
            else:
                num_priority_data[priority_num].append(0)
    stacked_data = np.array([np.array(value) for key, value in num_priority_data.items()])
    has_items = np.sum(stacked_data, axis=0)
    cut_off_index = len(has_items)
    for has_item in reversed(has_items):
        if has_item > 0:
            break
        cut_off_index += -1
    stacked_data = stacked_data[:, :cut_off_index]
    return stacked_data


def plot_stack_plot(stacked_data, name):
    X = np.arange(0, len(stacked_data[0]), 1)
    print(stacked_data[4])

    labels = ['storage', 'TopicOf', 'cMatch', 'seeAlso', 'contains', 'sameAs', 'typeIndex', 'SeedURL']
    plt.stackplot(X, *stacked_data, baseline="zero", labels = labels)
    plt.title(name)
    plt.axis('tight')
    plt.legend()
    plt.show()


def main():
    for i in range(0, 5):
        queue_contents = load_data("data/link_types_in_queue_no_prioritisation/queryDiscover{}.txt".format(i))
        plot_data = stack_link_type_occurrence_data(queue_contents)
        plot_stack_plot(plot_data, "Source of links in queue for discover-{}, without prioritisation".format(i))
        queue_contents = load_data("data/link_types_in_queue/queryDiscover{}.txt".format(i))
        plot_data = stack_link_type_occurrence_data(queue_contents)
        plot_stack_plot(plot_data, "Source of links in queue for discover-{}, with prioritisation".format(i))

    queue_contents = load_data("data/link_types_in_queue_no_prioritisation/queryDiscover5.txt")
    plot_data = stack_link_type_occurrence_data(queue_contents)
    plot_stack_plot(plot_data, "Source of links in queue for discover-5, without prioritisation")

if __name__ == "__main__":
    main()