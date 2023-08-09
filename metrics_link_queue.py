import numpy as np
import os
import ast
import json
import pandas as pd


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


def calculate_average_cmatch_contains_links(priority_type_dict, queue_content):
    cmatch_number = priority_type_dict['cMatch']
    contains_number = priority_type_dict['contains']
    prev_snapshot = []
    total_links_added = 0
    total_cmatch_added = 0
    total_contains_added = 0
    for snapshot in queue_content:
        if len(prev_snapshot) < len(snapshot):
            total_links_added += 1
            if snapshot[-1] == cmatch_number:
                total_cmatch_added += 1
            if snapshot[-1] == contains_number:
                total_contains_added += 1
        prev_snapshot = snapshot
    if total_links_added == 0:
        return 0, 0
    metric_cmatch = total_cmatch_added / total_links_added
    metric_contains = total_contains_added / total_links_added
    return metric_cmatch, metric_contains


def calculate_percentage_links(queue_contents, timestamps):
    time_multiple_links = 0
    time_at_least_one_link = 0
    total_time = timestamps[-1] - timestamps[0]
    for i in range(len(queue_contents) - 1):
        num_unique = len(set(queue_contents[i]))
        if num_unique > 1:
            time_multiple_links += timestamps[i + 1] - timestamps[i]
        if num_unique > 0:
            time_at_least_one_link += timestamps[i + 1] - timestamps[i]

    multiple_metric = time_multiple_links / total_time
    single_link_metric = time_at_least_one_link / total_time
    return multiple_metric, single_link_metric


def calculate_avg_number_type_links(queue_contents, timestamps):
    time_weighted_number_links = 0
    time_weighted_number_links_if_not_empty = 0
    total_time_multiple_links = 0
    total_time = timestamps[-1] - timestamps[0]
    for i in range(len(queue_contents) - 1):
        num_unique_links = len(set(queue_contents[i]))
        time_weighted_number_links += num_unique_links * (timestamps[i + 1] - timestamps[i])
        if num_unique_links > 0:
            time_weighted_number_links_if_not_empty += num_unique_links * (timestamps[i + 1] - timestamps[i])
            total_time_multiple_links += timestamps[i + 1] - timestamps[i]

    if total_time_multiple_links == 0:
        return 0, 0

    metric_time_avg_links = time_weighted_number_links / total_time
    metric_time_avg_links_if_not_empty = time_weighted_number_links_if_not_empty / total_time_multiple_links
    return metric_time_avg_links, metric_time_avg_links_if_not_empty


def divide_metrics_into_groups(metrics_list, division_index, cut_off):
    high_division_metric = [[], [], [], [], [], []]
    low_division_metric = [[], [], [], [], [], []]
    for i in range(len(metrics_list[0])):
        if metrics_list[division_index][i] > cut_off:
            for j in range(len(metrics_list)):
                high_division_metric[j].append(metrics_list[j][i])
        else:
            for z in range(len(metrics_list)):
                low_division_metric[z].append(metrics_list[z][i])
    return high_division_metric, low_division_metric


def calculate_mean_of_metrics(metrics_list):
    return [sum(x) / len(x) for x in metrics_list]


def calculate_all_metrics(dir_name):
    priority_type_dict = {"typeIndex": 1, "sameAs": 2, "seeAlso": 3, "storage": 4,
                          "isTopicOf": 5, "contains": 6, "cMatch": 7, "other": 8}
    avg_cmatch_metrics = []
    avg_contains_metrics = []
    avg_p_eff_metrics = []
    avg_p_one_link_metrics = []
    avg_links_metrics = []
    avg_links_not_empty_metrics = []
    file_names = []
    for [queue_content, timestamps, file] in load_dir_data(dir_name):
        print(file)
        avg_cmatch, avg_contains = calculate_average_cmatch_contains_links(priority_type_dict, queue_content)
        p_eff, p_one_link = calculate_percentage_links(queue_content, timestamps)
        avg_links, avg_links_not_empty = calculate_avg_number_type_links(queue_content, timestamps)

        avg_cmatch_metrics.append(avg_cmatch)
        avg_contains_metrics.append(avg_contains)
        avg_p_eff_metrics.append(p_eff)
        avg_p_one_link_metrics.append(p_one_link)
        avg_links_metrics.append(avg_links)
        avg_links_not_empty_metrics.append(avg_links_not_empty)
        short_name = '-'.join(file.split('.')[0].split('-')[1:])
        file_names.append(short_name)
    pd_dict = {'query': file_names, 'avgNumCMatch': avg_cmatch_metrics, 'avgNumContains': avg_contains_metrics,
               'pEff': avg_p_eff_metrics, 'pOneLink': avg_p_one_link_metrics, 'avgNumLinks': avg_links_metrics,
               'avgNumLinksNotEmtpy': avg_links_not_empty_metrics}
    df = pd.DataFrame(pd_dict)
    df = df.round(3)
    list_metrics = [avg_cmatch_metrics, avg_contains_metrics, avg_p_eff_metrics, avg_p_one_link_metrics,
                    avg_links_metrics, avg_links_not_empty_metrics]
    high, low = divide_metrics_into_groups(list_metrics, 3, .5)
    avg_metric_high = calculate_mean_of_metrics(high)
    avg_metric_low = calculate_mean_of_metrics(low)
    print(avg_metric_high)
    print(avg_metric_low)
    print(df.to_latex(index=False))


if __name__ == '__main__':
    calculate_all_metrics('data/link_queue_full')
