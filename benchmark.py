import sys

import numpy as np
from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5


def plot_with_confidence_intervals(results_dict, title, xlabel, ylabel):
    x_values = results_dict.keys()
    y_values = results_dict.values()

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)

    y_mean = np.mean(y_values)

    plt.axhline(y=y_mean, color='r', linestyle='--')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"experiment_{title}")


def run_benchmark_no_rules(num_runs):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        try:
            elapsed_time_no_rules = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time_no_rules
        except:
            continue

    plot_with_confidence_intervals(results, 'TCP No Rules', 'Run Number', 'Average Elapsed Time (s)')


def run_benchmark_packet_loss(num_runs, loss_percentage):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_loss(loss_percentage)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time
        except:
            continue

    plot_with_confidence_intervals(results, f'TCP Packet Loss {loss_percentage}%', 'Run Number', 'Average Elapsed Time (s)')


def run_benchmark_packet_corruption(num_runs, corruption):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_corruption(corruption)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time
        except:
            continue

    plot_with_confidence_intervals(results, f'TCP Packet Corruption {corruption}%', 'Run Number', 'Average Elapsed Time (s)')


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

    plot_with_confidence_intervals(results, f'TCP Delay (Uniform) {100}ms', 'Run Number',
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

    plot_with_confidence_intervals(results, f'TCP Delay (Normal) {100}ms', 'Run Number',
                                   'Average Elapsed Time (s)')


def run_benchmark_packet_duplication(num_runs, duplication):
    results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_duplication(duplication)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results[i] = elapsed_time
        except:
            continue

    plot_with_confidence_intervals(results, f'TCP Duplication {duplication}%', 'Run Number',
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
        for loss in [0, 5, 10, 15]:
            run_benchmark_packet_loss(num_benchmarks, loss)

    elif experiment_type == "corruption":
        for corruption in [0, 5, 10]:
            run_benchmark_packet_corruption(num_benchmarks, corruption)

    elif experiment_type == "delay_uniform":
        run_benchmark_packet_delay_uniform(num_benchmarks)

    elif experiment_type == "delay_normal":
        run_benchmark_packet_delay_normal(num_benchmarks)

    elif experiment_type == "duplication":
        for duplication in [0, 5, 10, 15]:
            run_benchmark_packet_duplication(num_benchmarks, duplication)
    else:
        print("[ERROR] Invalid experiment type.")
