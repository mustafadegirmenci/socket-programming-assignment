import tc
import tcpclient

PACKET_DELAY_JITTER = 5

if __name__ == "__main__":
    print(f"[INFO] Starting benchmark...\n")

    print(f"[INFO] Testing with no rules...\n")
    tc.clear_rules()
    elapsed_time_no_rules = tcpclient.request_files_and_measure_time(10)

    elapsed_time_packet_loss = {}
    for loss in [0, 5, 10, 15]:
        print(f"[INFO] Testing with {loss}% packet loss...\n")
        tc.clear_rules()
        tc.apply_packet_loss(loss)
        elapsed_time_packet_loss[loss] = tcpclient.request_files_and_measure_time(requested_file_count=10)

    elapsed_time_packet_corruption = {}
    for corruption in [0, 5, 10]:
        print(f"[INFO] Testing with {corruption}% packet corruption...\n")
        tc.clear_rules()
        tc.apply_packet_corruption(corruption)
        elapsed_time_packet_corruption[corruption] = tcpclient.request_files_and_measure_time(requested_file_count=10)

    print(f"[INFO] Testing with {100}ms packet delay and uniform distribution...\n")
    tc.clear_rules()
    tc.apply_packet_delay_uniform(100, PACKET_DELAY_JITTER)
    elapsed_time_packet_delay_uniform = tcpclient.request_files_and_measure_time(requested_file_count=10)

    print(f"[INFO] Testing with {100}ms packet delay and normal distribution...\n")
    tc.clear_rules()
    tc.apply_packet_delay_normal(100, PACKET_DELAY_JITTER)
    elapsed_time_packet_delay_normal = tcpclient.request_files_and_measure_time(requested_file_count=10)

    print(f"[INFO] Benchmark Results:\n")
    print(f"No Rules: \t{elapsed_time_no_rules}\n")

    for loss in elapsed_time_packet_loss.keys():
        print(f"Packet Loss ({loss}%): \t{elapsed_time_packet_loss[loss]}\n")

    for corruption in elapsed_time_packet_corruption.keys():
        print(f"Packet Corruption ({corruption}%): \t{elapsed_time_packet_corruption[corruption]}\n")

    print(f"Delay (Uniform): \t{elapsed_time_packet_delay_uniform}\n")
    print(f"Delay (Normal): \t{elapsed_time_packet_delay_normal}\n")
