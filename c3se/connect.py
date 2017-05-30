import subprocess
import json

# stack_name = ''
#
# with open('inventory.json', 'r') as f:
#     stack_info = json.load(f)
#     if 'stack_name' in a:
#         stack_name = stack_info['stack_name']

stack_name = 'test'
json_data = subprocess.Popen("openstack stack output show -f json --all " + stack_name, shell=True, stdout=subprocess.PIPE).stdout.read()

stack_info = json.loads(json_data)
ip = stack_info['hadoop_master_public_ip']
ip = json.loads(ip)
ip = ip['output_value']

args = ['ssh', 'ubuntu@' + ip, '-i', 'c3se_key.pem']
print(args)
subprocess.call(args)
