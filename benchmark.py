import sys

from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5


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

    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('TCP Packet Loss')
    plt.xlabel('Loss (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.savefig("tcp_loss")


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

    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('TCP Packet Corruption')
    plt.xlabel('Corruption (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.savefig("tcp_corruption")


def run_benchmark_packet_delay_uniform(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_uniform(100, PACKET_DELAY_JITTER)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results.append(elapsed_time)
        except:
            continue

    plt.figure(figsize=(6, 4))
    plt.bar(['Packet Delay (Uniform)'], [sum(results) / len(results)])
    plt.title('TCP Packet Delay (Uniform)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.savefig("tcp_delay_uniform")


def run_benchmark_packet_delay_normal(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_normal(100, PACKET_DELAY_JITTER)
        try:
            elapsed_time = tcpclient.request_files_and_measure_time(10)
            results.append(elapsed_time)
        except:
            continue

    plt.figure(figsize=(6, 4))
    plt.bar(['Packet Delay (Normal)'], [sum(results) / len(results)])
    plt.title('TCP Packet Delay (Normal)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.savefig("tcp_delay_normal")


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

    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('TCP Packet Duplication')
    plt.xlabel('Duplication (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.savefig("tcp_duplication")


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
