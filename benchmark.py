from matplotlib import pyplot as plt
import tc
import tcpclient

PACKET_DELAY_JITTER = 5
NUM_RUNS = 5  # Number of times to run the benchmark


def run_benchmark():
    results = {
        'no_rules': [],
        'packet_loss': {loss: [] for loss in [0, 5, 10, 15]},
        'packet_corruption': {corruption: [] for corruption in [0, 5, 10]},
        'packet_delay_uniform': [],
        'packet_delay_normal': []
    }

    for _ in range(NUM_RUNS):
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

    return results


def calculate_average(results):
    avg_results = {
        'no_rules': sum(results['no_rules']) / NUM_RUNS,
        'packet_loss': {loss: sum(times) / NUM_RUNS for loss, times in results['packet_loss'].items()},
        'packet_corruption': {corruption: sum(times) / NUM_RUNS for corruption, times in
                              results['packet_corruption'].items()},
        'packet_delay_uniform': sum(results['packet_delay_uniform']) / NUM_RUNS,
        'packet_delay_normal': sum(results['packet_delay_normal']) / NUM_RUNS
    }
    return avg_results


if __name__ == "__main__":
    print(f"[INFO] Starting benchmark...\n")
    benchmark_results = run_benchmark()
    average_results = calculate_average(benchmark_results)

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

    plt.tight_layout()
    plt.savefig('plot.png')
