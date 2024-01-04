import subprocess

DEFAULT_INTERFACE = "eth0"


def apply_packet_loss(loss_percentage, interface=DEFAULT_INTERFACE):
    command = f"tc qdisc add dev {interface} root netem loss {loss_percentage}%"
    subprocess.run(command, shell=True)


def apply_packet_duplication(duplication_percentage, interface=DEFAULT_INTERFACE):
    subprocess.run(f"tc qdisc add dev {interface} root netem duplicate {duplication_percentage}%", shell=True)


def apply_packet_corruption(corruption_percentage, interface=DEFAULT_INTERFACE):
    command = f"tc qdisc add dev {interface} root netem corrupt {corruption_percentage}%"
    subprocess.run(command, shell=True)


def apply_packet_delay_uniform(delay_time, interface=DEFAULT_INTERFACE):
    command = f"tc qdisc add dev {interface} root netem delay {delay_time}ms"
    subprocess.run(command, shell=True)


def apply_packet_delay_normal(delay_time, interface=DEFAULT_INTERFACE):
    command = f"tc qdisc add dev {interface} root netem delay {delay_time}ms distribution normal"
    subprocess.run(command, shell=True)


def clear_tc_rules(interface=DEFAULT_INTERFACE):
    command = f"tc qdisc del dev {interface} root"
    subprocess.run(command, shell=True)


apply_packet_loss(20)
clear_tc_rules()

apply_packet_duplication(20)
clear_tc_rules()

apply_packet_corruption(20)
clear_tc_rules()

apply_packet_delay_uniform(20)
clear_tc_rules()

apply_packet_delay_normal(30)
clear_tc_rules()
