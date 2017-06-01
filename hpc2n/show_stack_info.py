import subprocess

with open('stack_name', 'r') as f:
    stack_name = f.readline().strip()

command_str = "openstack stack output show --all " + stack_name
subprocess.Popen(command_str, shell=True).wait()
