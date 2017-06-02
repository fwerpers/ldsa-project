import subprocess
import os

inventory_path = os.path.join('inventory', 'hosts')
command_str = "ansible-playbook -i " + inventory_path + " playbook.yml -v -c paramiko"
subprocess.Popen(command_str, shell=True).wait()
