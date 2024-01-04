import subprocess

command = "sudo tc qdisc change dev eth2 root netem loss 5%"

try:
    subprocess.run(command, shell=True, check=True, executable="/bin/bash")
    print("Command executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Command execution failed: {e}")