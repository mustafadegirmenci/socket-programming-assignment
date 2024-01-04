import tc
import tcpclient

if __name__ == "__main__":
    print(f"[INFO] Starting benchmark...\n")

    print(f"[INFO] Testing with no rules...\n")
    elapsed_time_no_rules = tcpclient.request_files_and_measure_time(10)

    print(f"[INFO] Testing with 0% packet loss...\n")
    tc.apply_packet_loss(0)
    elapsed_time_packet_loss_0 = tcpclient.request_files_and_measure_time(10)

    print(f"[INFO] Testing with 5% packet loss...\n")
    tc.clear_rules()
    tc.apply_packet_loss(5)
    elapsed_time_packet_loss_5 = tcpclient.request_files_and_measure_time(10)

    print(f"[INFO] Testing with 10% packet loss...\n")
    tc.clear_rules()
    tc.apply_packet_loss(10)
    elapsed_time_packet_loss_10 = tcpclient.request_files_and_measure_time(10)

    print(f"[INFO] Testing with 15% packet loss...\n")
    tc.clear_rules()
    tc.apply_packet_loss(15)
    elapsed_time_packet_loss_15 = tcpclient.request_files_and_measure_time(10)

