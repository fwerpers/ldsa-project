import subprocess
import os

inventory_path = os.path.join('../inventory', 'hosts-pro')
command_str = "ansible-playbook -i " + inventory_path + " playbook.yml"
subprocess.Popen(command_str, shell=True).wait()
