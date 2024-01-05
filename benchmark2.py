import sys

from matplotlib import pyplot as plt
import tc
import udpclient2

PACKET_DELAY_JITTER = 5


def run_benchmark_no_rules(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        elapsed_time_no_rules = udpclient2.receive_all_files()
        results.append(elapsed_time_no_rules)

    return results


def run_benchmark_packet_loss(num_runs, losses):
    results = {loss: [] for loss in losses}

    for loss in losses:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_loss(loss)
            elapsed_time = udpclient2.receive_all_files()
            results[loss].append(elapsed_time)

    return results


def run_benchmark_packet_corruption(num_runs, corruptions):
    results = {corruption: [] for corruption in corruptions}

    for corruption in corruptions:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_corruption(corruption)
            elapsed_time = udpclient2.receive_all_files()
            results[corruption].append(elapsed_time)

    return results


def run_benchmark_packet_delay_uniform(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_uniform(100, PACKET_DELAY_JITTER)
        elapsed_time = udpclient2.receive_all_files()
        results.append(elapsed_time)

    return results


def run_benchmark_packet_delay_normal(num_runs):
    results = []

    for _ in range(num_runs):
        tc.clear_rules()
        tc.apply_packet_delay_normal(100, PACKET_DELAY_JITTER)
        elapsed_time = udpclient2.receive_all_files()
        results.append(elapsed_time)

    return results


def run_benchmark_packet_duplication(num_runs, duplications):
    results = {duplication: [] for duplication in duplications}

    for duplication in duplications:
        for _ in range(num_runs):
            tc.clear_rules()
            tc.apply_packet_duplication(duplication)
            elapsed_time = udpclient2.receive_all_files()
            results[duplication].append(elapsed_time)

    return results


def plot_packet_loss(results):
    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('Packet Loss')
    plt.xlabel('Loss (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_packet_corruption(results):
    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('Packet Corruption')
    plt.xlabel('Corruption (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_packet_delay_uniform(results):
    plt.figure(figsize=(6, 4))
    plt.bar(['Packet Delay (Uniform)'], [sum(results) / len(results)])
    plt.title('Packet Delay (Uniform)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_packet_delay_normal(results):
    plt.figure(figsize=(6, 4))
    plt.bar(['Packet Delay (Normal)'], [sum(results) / len(results)])
    plt.title('Packet Delay (Normal)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_packet_duplication(results):
    plt.figure(figsize=(6, 4))
    plt.plot(list(results.keys()), [sum(times) / len(times) for times in results.values()], marker='o')
    plt.title('Packet Duplication')
    plt.xlabel('Duplication (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] Usage: python script_name.py <num_benchmarks>")
        sys.exit(1)

    num_benchmarks = int(sys.argv[1])

    print(f"[INFO] Starting {num_benchmarks} benchmark{'s' if num_benchmarks > 1 else ''}...\n")

    losses_to_test = [0, 5, 10, 15]
    packet_loss_results = run_benchmark_packet_loss(num_benchmarks, losses_to_test)
    plot_packet_loss(packet_loss_results)

    corruptions_to_test = [0, 5, 10]
    packet_corruption_results = run_benchmark_packet_corruption(num_benchmarks, corruptions_to_test)
    plot_packet_corruption(packet_corruption_results)

    packet_delay_uniform_results = run_benchmark_packet_delay_uniform(num_benchmarks)
    plot_packet_delay_uniform(packet_delay_uniform_results)

    packet_delay_normal_results = run_benchmark_packet_delay_normal(num_benchmarks)
    plot_packet_delay_normal(packet_delay_normal_results)

    duplications_to_test = [0, 5, 10, 15]
    packet_duplication_results = run_benchmark_packet_duplication(num_benchmarks, duplications_to_test)
    plot_packet_duplication(packet_duplication_results)
