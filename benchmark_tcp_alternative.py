import sys

from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5


def plot_with_confidence_intervals(results_dict, title, xlabel, ylabel):
    x_values = results_dict.keys()
    y_values = results_dict.values()

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"experiment_{title}")


def run_benchmark_packet_loss(num_runs, loss_list):
    list_results = {}

    for loss in loss_list:
        tc.clear_rules()
        tc.apply_packet_loss(loss)
        for i in range(num_runs):
            try:
                elapsed_time = tcpclient.request_files_and_measure_time(10)
                list_results[loss].append(elapsed_time)
            except:
                continue

    results = {}
    for key in list_results.keys():
        val = list_results[key]
        results[key] = sum(val) / len(val)

    print(results)
    plot_with_confidence_intervals(results, f'TCP Packet Loss - Alternative', 'Loss (%)', 'Average Elapsed Time (s)')


def run_benchmark_packet_corruption(num_runs, corruption_list):
    list_results = {}

    for corruption in corruption_list:
        tc.clear_rules()
        tc.apply_packet_corruption(corruption)
        for i in range(num_runs):
            try:
                elapsed_time = tcpclient.request_files_and_measure_time(10)
                list_results[corruption].append(elapsed_time)
            except:
                continue

    results = {}
    for key in list_results.keys():
        val = list_results[key]
        results[key] = sum(val) / len(val)
    plot_with_confidence_intervals(results, f'TCP Packet Corruption {corruption}%', 'Corruption (%) - Alternative', 'Average Elapsed Time (s)')


def run_benchmark_packet_duplication(num_runs, duplication):
    list_results = {}

    for i in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_duplication(duplication)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            list_results[i].append(elapsed_time)
        except:
            continue

    results = {}
    for key in list_results.keys():
        val = list_results[key]
        results[key] = sum(val) / len(val)

    plot_with_confidence_intervals(results, f'TCP Duplication {duplication}% - Alternative', 'Duplication (%)',
                                   'Average Elapsed Time (s)')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("[ERROR] Usage: python script_name.py <num_benchmarks> <experiment_type>")
        sys.exit(1)

    num_benchmarks = int(sys.argv[1])
    experiment_type = str(sys.argv[2])

    print(f"[INFO] Starting {num_benchmarks} benchmark{'s' if num_benchmarks > 1 else ''} for {experiment_type}...\n")

    if experiment_type == "loss":
        run_benchmark_packet_loss(num_benchmarks, [0, 5, 10, 15])

    elif experiment_type == "corruption":
        run_benchmark_packet_corruption(num_benchmarks, [0, 5, 10])

    elif experiment_type == "duplication":
        run_benchmark_packet_duplication(num_benchmarks, [0, 5, 10, 15])
    else:
        print("[ERROR] Invalid experiment type.")
