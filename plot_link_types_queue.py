import ast
from collections import Counter
import pylab as plt
import numpy as np
import os
import json
import matplotlib


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


def load_full_queue_data(location):
    with open(location) as f:
        return json.load(f)


def load_dir_data(dir_name):
    files = os.listdir(dir_name)
    for file in files:
        data = load_full_queue_data('{}/{}'.format(dir_name, file))
        link_queue_content = ast.literal_eval(data.get('linkQueueContent'))
        timestamps = ast.literal_eval(data.get('timeStamps'))
        yield link_queue_content, timestamps, file


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


def plot_stack_plot(stacked_data, name, labels, save):
    X = np.arange(0, len(stacked_data[0]), 1)

    plt.stackplot(X, *stacked_data, baseline="zero", labels=labels,
                  colors=['blue', 'green', 'red', 'purple', 'brown', 'pink', 'grey', 'lime'])
    plt.title(name.split('.')[0])
    plt.axis('tight')
    plt.legend()
    if save:
        plt.savefig('plots_new/{}.svg'.format(name.split('.')[0]))
    plt.show()


def plot_stack_plot_timestamp(stacked_data, timestamps, name, labels, save):
    formatted_name = 'Query ' + ('-'.join(name.split('.')[0].split('-')[1:]).capitalize())
    print(formatted_name)
    plt.stackplot(timestamps, *stacked_data, baseline="zero", labels=labels,
                  colors=['blue', 'green', 'red', 'purple', 'brown', 'pink', 'grey', 'lime'])
    plt.title(formatted_name)
    plt.axis('tight')
    plt.legend()
    if save:
        plt.savefig('plots_shortened/{}-timestamps.svg'.format(name.split('.')[0]))
    plt.show()


def center_time_at_zero(timestamps):
    return [x - timestamps[0] for x in timestamps]


def cut_off_time_after_timeout(time, queue_content, timeout):
    cutoff = find_cutoff_index(time, timeout)
    if cutoff == len(time) - 1:
        return time, queue_content
    time_cut = time[:cutoff]
    queue_content_cut = queue_content[:, :cutoff]
    print(len(time))
    print(queue_content.shape)
    return time_cut, queue_content_cut


def find_cutoff_index(time, timeout):
    index = 0
    for i in range(len(time)):
        if time[i] > timeout:
            return i
        index = i
    return index


def plot_in_dir(dir_name, dir_name_timestamps):
    labelsTypeSource = ['typeIndex', 'sameAs', 'seeAlso', 'storage', 'isTopicOf', 'contains', 'cMatch', 'SeedURL']
    files = os.listdir(dir_name)
    files_timestamps = os.listdir(dir_name_timestamps)
    for file, file_timestamps in zip(files, files_timestamps):
        queue_content = load_data(dir_name + '/' + file)
        timestamps = load_data(dir_name_timestamps + '/' + file_timestamps)
        plot_data = stack_link_type_occurrence_data_timestamp_based(queue_content)
        plot_data_non_ts = stack_link_type_occurrence_data(queue_content)
        try:
            plot_stack_plot_timestamp(plot_data, center_time_at_zero(timestamps), file, labelsTypeSource, False)
        except ValueError:
            print(plot_data.shape)
            print(len(timestamps))

        # plot_stack_plot(plot_data_non_ts, file, labelsTypeSource, False)


def main():
    plot_in_dir('data/test',
                'data/test_timestamps')
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


def main_plot(dir_name):
    labelsTypeSource = ['typeIndex', 'sameAs', 'seeAlso', 'storage', 'isTopicOf', 'contains', 'cMatch', 'SeedURL']
    for [queue_content, timestamps, file] in load_dir_data(dir_name):
        plot_data = stack_link_type_occurrence_data_timestamp_based(queue_content)
        plot_data_non_ts = stack_link_type_occurrence_data(queue_content)
        plot_stack_plot(plot_data_non_ts, file, labelsTypeSource, False)
        try:
            time, queue_content_cut = cut_off_time_after_timeout(center_time_at_zero(timestamps), plot_data, 80)
            plot_stack_plot_timestamp(queue_content_cut, time, file, labelsTypeSource, False)
            # plot_stack_plot_timestamp(plot_data, center_time_at_zero(timestamps), file, labelsTypeSource, True)
        except ValueError:
            print(plot_data.shape)
            print(len(timestamps))


def plot_stack_plot_timestamp_multi(stacked_data, timestamps, names, labels, save):
    fig, axes = plt.subplots(3, 2, figsize=(20, 20))
    # axes[2][1].set_visible(False)
    # chartBox = axes[2][0].get_position()
    # axes[2][0].set_position([chartBox.x0 + 0.215, chartBox.y0, chartBox.width, chartBox.height])
    row = 0
    col = 0
    print(len(stacked_data))
    for data, ts, name in zip(stacked_data, timestamps, names):
        formatted_name = 'Query ' + ('-'.join(name.split('.')[0].split('-')[1:]).capitalize())
        axes[row][col].stackplot(ts, *data, baseline="zero", labels=labels,
                                 colors=['blue', 'green', 'red', 'purple', 'brown', 'pink', 'grey', 'lime'])
        axes[row][col].set_title(formatted_name)
        axes[row][col].axis('tight')
        # axes[row][col].legend()

        if col == 1:
            col = 0
            row += 1
        else:
            col += 1

    # fig.tight_layout()
    fig.legend(labels, loc='upper right', bbox_to_anchor=(0.785, 0.98), ncol=4, bbox_transform=fig.transFigure)
    fig.show()

    # axes[2][1].set_position([0.55, 0.125, 0.228, 0.343])
    # formatted_name = 'Query ' + ('-'.join(name.split('.')[0].split('-')[1:]).capitalize())
    # print(formatted_name)
    # plt.stackplot(timestamps, *stacked_data, baseline="zero", labels=labels,
    #               colors=['blue', 'green', 'red', 'purple', 'brown', 'pink', 'grey', 'lime'])
    # plt.title(formatted_name)
    # plt.axis('tight')
    # plt.legend()
    if save:
        fig.savefig('multi_plots/{}.svg'.format("multi_plot"))
    # plt.show()


def main_plot_multi_plot(dir_name):
    matplotlib.rcParams.update({'font.size': 24})
    labelsTypeSource = ['typeIndex', 'sameAs', 'seeAlso', 'storage', 'isTopicOf', 'contains', 'cMatch', 'SeedURL']
    queue_content_list = []
    timestamps_list = []
    file_list = []

    # for [queue_content, timestamps, file] in load_dir_data(dir_name):
    #     plot_data = stack_link_type_occurrence_data_timestamp_based(queue_content)
    #     plot_data_non_ts = stack_link_type_occurrence_data(queue_content)
    #     plot_stack_plot(plot_data_non_ts, file, labelsTypeSource, False)
    #     try:
    #         time, queue_content_cut = cut_off_time_after_timeout(center_time_at_zero(timestamps), plot_data, 80)
    #         plot_stack_plot_timestamp(queue_content_cut, time, file, labelsTypeSource, False)
    #         # plot_stack_plot_timestamp(plot_data, center_time_at_zero(timestamps), file, labelsTypeSource, True)
    #     except ValueError:
    #         print(plot_data.shape)
    #         print(len(timestamps))

    for i, [queue_content, timestamps, file] in enumerate(load_dir_data(dir_name)):
        if i != 0:
            stacked_queue_content = stack_link_type_occurrence_data_timestamp_based(queue_content)
            time, queue_content_cut = cut_off_time_after_timeout(center_time_at_zero(timestamps), stacked_queue_content, 60)
            queue_content_list.append(queue_content_cut)
            timestamps_list.append(time)
            file_list.append(file)
        else:
            stacked_queue_content = stack_link_type_occurrence_data_timestamp_based(queue_content)
            queue_content_list.append(stacked_queue_content)
            timestamps_list.append(center_time_at_zero(timestamps))
            file_list.append(file)


    complex_2_queue_content = queue_content_list.pop(0)
    complex_2_ts = timestamps_list.pop(0)
    complex_2_file = file_list.pop(0)
    time, queue_content_cut = cut_off_time_after_timeout(center_time_at_zero(complex_2_ts), complex_2_queue_content, 80)
    queue_content_list.append(queue_content_cut)
    queue_content_list.append(complex_2_queue_content)
    timestamps_list.append(time)
    timestamps_list.append(complex_2_ts)
    file_list.append(complex_2_file)
    file_list.append(complex_2_file)

    plot_stack_plot_timestamp_multi(queue_content_list, timestamps_list, file_list, labelsTypeSource, True)
    #


if __name__ == "__main__":
    # main_plot('data/link_queue_full_80_timeout')
    # main()
    main_plot_multi_plot('data/link_queue_multi_plot')
    pass
