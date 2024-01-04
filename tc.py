import subprocess

DEFAULT_INTERFACE = "eth0"


def apply_packet_loss(loss_percentage, interface=DEFAULT_INTERFACE):
    print(f"[INFO] Setting packet loss to {loss_percentage}%...\n")
    command = f"tc qdisc add dev {interface} root netem loss {loss_percentage}%"
    subprocess.run(command, shell=True)


def clear_rules(interface=DEFAULT_INTERFACE):
    print(f"[INFO] Clearing TC rules...\n")
    command = f"tc qdisc del dev {interface} root"
    subprocess.run(command, shell=True)


def show_active_rules():
    print(f"[INFO] Showing TC rules...\n")
    command = "tc qdisc show"
    subprocess.run(command, shell=True)


apply_packet_loss(20)
show_active_rules()

clear_rules()
show_active_rules()
