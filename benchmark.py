import sys

import numpy as np
from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5


def plot_with_confidence_intervals(x_values, y_values_dict, title, xlabel, ylabel):
    means = [np.mean(times) for times in y_values_dict.values()]
    std_err = [1.96 * np.std(list(times)) / np.sqrt(len(list(times))) for times in y_values_dict.values()]

    plt.figure(figsize=(6, 4))
    plt.errorbar(x_values, means, yerr=std_err, fmt='o', capsize=5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.tight_layout()

    plt.savefig(f"tcp_{title.lower().replace(' ', '_')}")


def run_benchmark_no_rules(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        try:
            elapsed_time_no_rules = tcpclient.request_files_and_measure_time(10)
            results.append(elapsed_time_no_rules)
        except:
            continue

    plt.figure(figsize=(8, 6))
    plt.plot(range(1, num_runs + 1), results, marker='o', linestyle='-')
    plt.xlabel('Run Number')
    plt.ylabel('Elapsed Time')
    plt.title('TCP No Rules')
    plt.grid(True)
    plt.savefig("tcp_norules")


def run_benchmark_packet_loss(num_runs, losses):
    results = {loss: [] for loss in losses}

    for loss in losses:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_loss(loss)
            try:
                elapsed_time = tcpclient.request_files_and_measure_time(10)
                results[loss].append(elapsed_time)
            except:
                continue

    plot_with_confidence_intervals(list(results.keys()), results, 'TCP Packet Loss', 'Loss (%)', 'Average Elapsed Time (s)')


def run_benchmark_packet_corruption(num_runs, corruptions):
    results = {corruption: [] for corruption in corruptions}

    for corruption in corruptions:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_corruption(corruption)
            try:
                elapsed_time = tcpclient.request_files_and_measure_time(10)
                results[corruption].append(elapsed_time)
            except:
                continue

    plot_with_confidence_intervals(list(results.keys()), results, 'TCP Packet Corruption', 'Corruption (%)', 'Average Elapsed Time (s)')


def run_benchmark_packet_delay_uniform(num_runs):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_uniform(100, PACKET_DELAY_JITTER)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time
        except:
            continue

    plot_with_confidence_intervals(list(results.keys()), results, 'TCP Delay (Uniform)', 'Delay (%)',
                                   'Average Elapsed Time (s)')


def run_benchmark_packet_delay_normal(num_runs):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_normal(100, PACKET_DELAY_JITTER)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time
        except:
            continue

    plot_with_confidence_intervals(list(results.keys()), results, 'TCP Delay (Normal)', 'Delay (%)',
                                   'Average Elapsed Time (s)')


def run_benchmark_packet_duplication(num_runs, duplications):
    results = {duplication: [] for duplication in duplications}

    for duplication in duplications:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_duplication(duplication)
            try:
                elapsed_time = tcpclient.request_files_and_measure_time(10)
                results[duplication].append(elapsed_time)
            except:
                continue

    plot_with_confidence_intervals(list(results.keys()), results, 'TCP Duplication', 'Duplication (%)',
                                   'Average Elapsed Time (s)')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("[ERROR] Usage: python script_name.py <num_benchmarks> <experiment_type>")
        sys.exit(1)

    num_benchmarks = int(sys.argv[1])
    experiment_type = str(sys.argv[2])

    print(f"[INFO] Starting {num_benchmarks} benchmark{'s' if num_benchmarks > 1 else ''} for {experiment_type}...\n")

    if experiment_type == "norules":
        run_benchmark_no_rules(num_benchmarks)
    elif experiment_type == "loss":
        losses_to_test = [0, 5, 10, 15]
        run_benchmark_packet_loss(num_benchmarks, losses_to_test)
    elif experiment_type == "corruption":
        corruptions_to_test = [0, 5, 10]
        run_benchmark_packet_corruption(num_benchmarks, corruptions_to_test)
    elif experiment_type == "delay_uniform":
        run_benchmark_packet_delay_uniform(num_benchmarks)
    elif experiment_type == "delay_normal":
        run_benchmark_packet_delay_normal(num_benchmarks)
    elif experiment_type == "duplication":
        duplications_to_test = [0, 5, 10, 15]
        run_benchmark_packet_duplication(num_benchmarks, duplications_to_test)
    else:
        print("[ERROR] Invalid experiment type.")
