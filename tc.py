import subprocess

command = "tc qdisc add dev eth0 root netem delay 100ms 50ms"

try:
    subprocess.run(command, shell=True, check=True, executable="/bin/bash")
    print("Command executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Command execution failed: {e}")