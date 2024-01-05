import sys

from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5


def run_benchmark(num_runs):
    results = {
        'no_rules': [],
        'packet_loss': {loss: [] for loss in [0, 5, 10, 15]},
        'packet_corruption': {corruption: [] for corruption in [0, 5, 10]},
        'packet_delay_uniform': [],
        'packet_delay_normal': [],
        'packet_duplication': {duplication: [] for duplication in [0, 5, 10, 15]}
    }

    for _ in range(num_runs):
        tc.clear_rules()

        # No rules test
        elapsed_time_no_rules = tcpclient.request_files_and_measure_time(10)
        results['no_rules'].append(elapsed_time_no_rules)

        # Packet Loss tests
        for loss in [0, 5, 10, 15]:
            tc.clear_rules()
            tc.apply_packet_loss(loss)
            elapsed_time = tcpclient.request_files_and_measure_time(requested_file_count=10)
            results['packet_loss'][loss].append(elapsed_time)

        # Packet Corruption tests
        for corruption in [0, 5, 10]:
            tc.clear_rules()
            tc.apply_packet_corruption(corruption)
            elapsed_time = tcpclient.request_files_and_measure_time(requested_file_count=10)
            results['packet_corruption'][corruption].append(elapsed_time)

        # Packet Delay (Uniform)
        tc.clear_rules()
        tc.apply_packet_delay_uniform(100, PACKET_DELAY_JITTER)
        elapsed_time = tcpclient.request_files_and_measure_time(requested_file_count=10)
        results['packet_delay_uniform'].append(elapsed_time)

        # Packet Delay (Normal)
        tc.clear_rules()
        tc.apply_packet_delay_normal(100, PACKET_DELAY_JITTER)
        elapsed_time = tcpclient.request_files_and_measure_time(requested_file_count=10)
        results['packet_delay_normal'].append(elapsed_time)

        for duplication in [0, 5, 10]:
            tc.clear_rules()
            tc.apply_packet_duplication(duplication)
            elapsed_time = tcpclient.request_files_and_measure_time(requested_file_count=10)
            results['packet_duplication'][duplication].append(elapsed_time)

    return results


def calculate_average(results, num_runs):
    avg_results = {
        'no_rules': sum(results['no_rules']) / num_runs,
        'packet_loss': {loss: sum(times) / num_runs for loss, times in results['packet_loss'].items()},
        'packet_corruption': {corruption: sum(times) / num_runs for corruption, times in
                              results['packet_corruption'].items()},
        'packet_delay_uniform': sum(results['packet_delay_uniform']) / num_runs,
        'packet_delay_normal': sum(results['packet_delay_normal']) / num_runs,
        'packet_duplication': {duplication: sum(times) / num_runs for duplication, times in
                               results['packet_duplication'].items()}

    }
    return avg_results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[WARNING] Usage: python script_name.py <num_benchmarks>")
        num_benchmarks = 1
    else:
        num_benchmarks = int(sys.argv[1])

    print(f"[INFO] Starting {num_benchmarks} benchmark{'s' if num_benchmarks > 1 else ''}...\n")
    benchmark_results = run_benchmark(num_benchmarks)
    average_results = calculate_average(benchmark_results, num_benchmarks)

    print("[INFO] Average Benchmark Results:\n")
    print(f"No Rules: \t{average_results['no_rules']}\n")

    for loss, avg_time in average_results['packet_loss'].items():
        print(f"Packet Loss ({loss}%): \t{avg_time}\n")

    for corruption, avg_time in average_results['packet_corruption'].items():
        print(f"Packet Corruption ({corruption}%): \t{avg_time}\n")

    print(f"Delay (Uniform): \t{average_results['packet_delay_uniform']}\n")
    print(f"Delay (Normal): \t{average_results['packet_delay_normal']}\n")

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 2, 1)
    plt.plot(list(average_results['packet_loss'].keys()), list(average_results['packet_loss'].values()), marker='o')
    plt.title('Packet Loss')
    plt.xlabel('Loss (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()

    plt.subplot(2, 2, 2)
    plt.plot(list(average_results['packet_corruption'].keys()), list(average_results['packet_corruption'].values()),
             marker='o')
    plt.title('Packet Corruption')
    plt.xlabel('Corruption (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()

    plt.subplot(2, 2, 3)
    plt.bar(['No Rules', 'Uniform Delay', 'Normal Delay'],
            [average_results['no_rules'], average_results['packet_delay_uniform'],
             average_results['packet_delay_normal']])
    plt.title('Packet Delay')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()

    plt.subplot(2, 3, 5)  # Update subplot index accordingly
    plt.plot(list(average_results['packet_duplication'].keys()), list(average_results['packet_duplication'].values()),
             marker='o')
    plt.title('Packet Duplication')
    plt.xlabel('Duplication (%)')
    plt.ylabel('Average Elapsed Time (s)')
    plt.grid()

    plt.tight_layout()
    plt.savefig('plot.png')
