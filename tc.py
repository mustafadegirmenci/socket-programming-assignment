import subprocess

DEFAULT_INTERFACE = "eth0"


def apply_packet_loss(loss_percentage, interface=DEFAULT_INTERFACE):
    print(f"[INFO] Setting packet loss to {loss_percentage}%...\n")
    command = f"tc qdisc add dev {interface} root netem loss {loss_percentage}%"
    subprocess.run(command, shell=True)


def apply_packet_delay_normal(delay, jitter, interface=DEFAULT_INTERFACE):
    print(f"[INFO] Setting packet delay to {delay}ms {jitter}ms with normal distribution...\n")
    command = f"tc qdisc add dev {interface} root netem delay {delay}ms {jitter}ms distribution normal"
    subprocess.run(command, shell=True)


def apply_packet_delay_uniform(delay, jitter, interface=DEFAULT_INTERFACE):
    print(f"[INFO] Setting packet delay to {delay}ms {jitter}ms with uniform distribution...\n")
    command = f"tc qdisc add dev {interface} root netem delay {delay}ms {jitter}ms"
    subprocess.run(command, shell=True)


def apply_packet_corruption(corruption_percentage, interface=DEFAULT_INTERFACE):
    print(f"[INFO] Setting packet corruption to {corruption_percentage}%...\n")
    command = f"tc qdisc add dev {interface} root netem corrupt {corruption_percentage}%"
    subprocess.run(command, shell=True)


def clear_rules(interface=DEFAULT_INTERFACE):
    print(f"[INFO] Clearing TC rules...\n")
    command = f"tc qdisc del dev {interface} root"
    subprocess.run(command, shell=True)


def show_active_rules():
    print(f"[INFO] Showing TC rules...\n")
    command = "tc qdisc show"
    subprocess.run(command, shell=True)
