import subprocess
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

inventory_path = os.path.join('inventory', 'hosts')
command_str = "ansible-playbook -i " + inventory_path + " playbook.yml" + " -c paramiko"
subprocess.Popen(command_str, shell=True).wait()
