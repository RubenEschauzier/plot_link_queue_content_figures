import ast
from collections import Counter
import pylab as plt
import numpy as np
import os


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
    priorities = range(1, 9)  # [1, 2, ..., 8] iterator
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

def stack_link_type_occurrence_data_timestamp_based(list_link_priorities):
    priorities = range(1, 9)  # [1, 2, ..., 8] iterator
    num_priority_data = {p: [] for p in priorities}  # or just {p: [] for p in range(0, 7)}

    for priority_count in list_link_priorities:
        counts = Counter(priority_count)
        for priority_num in priorities:
            if counts.get(priority_num):
                num_priority_data[priority_num].append(counts.get(priority_num))
            else:
                num_priority_data[priority_num].append(0)
    stacked_data = np.array([np.array(value) for key, value in num_priority_data.items()])
    return stacked_data



def plot_stack_plot(stacked_data, name, labels):
    X = np.arange(0, len(stacked_data[0]), 1)

    plt.stackplot(X, *stacked_data, baseline="zero", labels=labels)
    plt.title(name)
    plt.axis('tight')
    plt.legend()
    plt.show()


def plot_stack_plot_timestamp(stacked_data, timestamps, name, labels):
    print(stacked_data.shape)

    plt.stackplot(timestamps, *stacked_data, baseline="zero", labels=labels)
    plt.title(name)
    plt.axis('tight')
    plt.legend()
    plt.show()


def center_time_at_zero(timestamps):
    return [x - timestamps[0] for x in timestamps]


def plot_in_dir(dir_name, dir_name_timestamps):
    labelsTypeSource = ['typeIndex', 'sameAs', 'seeAlso', 'storage', 'isTopicOf', 'contains', 'cMatch', 'SeedURL']
    files = os.listdir(dir_name)
    files_timestamps = os.listdir(dir_name_timestamps)
    for file, file_timestamps in zip(files, files_timestamps):
        queue_content = load_data(dir_name+'/'+file)
        timestamps = load_data(dir_name_timestamps+'/'+file_timestamps)
        plot_data = stack_link_type_occurrence_data_timestamp_based(queue_content)
        # plot_data_non_ts = stack_link_type_occurrence_data(queue_content)
        print("Start")
        print(len(queue_content))
        print(len(timestamps))
        plot_stack_plot_timestamp(plot_data, center_time_at_zero(timestamps), file, labelsTypeSource)
        # plot_stack_plot(plot_data_non_ts, file, labelsTypeSource)

def main():
    plot_in_dir('data/test', 'data/test_timestamps')
    # for i in range(1, 9):
    #     queue_contents = load_data(
    #         "data/link_queue_content_no_prioritisation/interactive-discover-{}.sparql.txt".format(i))
    #     timestamps = load_data(
    #         "data/link_queue_content_prioritisation/interactive-discover-{}.sparql.timestamps.txt".format(i))
    #     print(center_time_at_zero(timestamps))
    #     plot_data = stack_link_type_occurrence_data(queue_contents)
    #     plot_stack_plot(plot_data, "Source of links in queue for discover-{}, with prioritisation".format(i),
    #                     labelsTypeSource)
        # queue_contents = load_data("data/link_types_in_queue/queryDiscover{}.txt".format(i))
        # plot_data = stack_link_type_occurrence_data(queue_contents)
        # plot_stack_plot(plot_data, "Source of links in queue for discover-{}, with prioritisation".format(i))


if __name__ == "__main__":
    main()
