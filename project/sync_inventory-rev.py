import json
from string import Template
import subprocess
import utils
import os
import yaml

HADOOP_MASTER_PUBLIC_KEY = "hadoop_master_public_ip"
HADOOP_MASTER_PRIVATE_KEY = "hadoop_master_private_ip"
HADOOP_DATANODE_PRIVATE_KEY = "nodes_private_ips"

ANSIBLE_SSH_USER = "ubuntu"

ANSIBLE_SSH_PRIVATE_KEY_FILE = "~/.ssh/hadoop_key.pem"

HOST_TEMPLATE = Template('$ipaddress ansible_connection=ssh ansible_user=$ssh_user ansible_ssh_private_key_file=$private_key_file')

def parse_stack_info(string):

    def parse(d):
        for key in d.keys():
            try:
                next_d = json.loads(d[key])
                val = parse(next_d)
            except TypeError:
                continue
            except ValueError:
                val = d[key]
            d[key] = val

        return(d)

    base_dict = json.loads(string)
    return(parse(base_dict))

class InventorySyncer:
    def __init__(self):
        stack_name = utils.get_stack_name()
        json_data = subprocess.Popen("openstack stack output show -f json --all " + stack_name, shell=True, stdout=subprocess.PIPE).stdout.read()
        self.stack_info = parse_stack_info(json_data)

    def update_master_setup_inventory(self):
        inventory_path = os.path.join('ansible', 'master_setup', 'inventory')
        with open(os.path.join(inventory_path, 'inventory_template'), 'r') as f:
            template = Template(f.read())

        ip_address = self.stack_info.get(HADOOP_MASTER_PUBLIC_KEY).get('output_value')
        key_path = utils.get_key_path()
        host_entry = HOST_TEMPLATE.substitute(
            ipaddress=ip_address,
            ssh_user=ANSIBLE_SSH_USER,
            private_key_file=key_path
        )

        inventory = template.substitute(
            master_host=host_entry,
            key_path=key_path
        )

        with open(os.path.join(inventory_path, 'hosts'), 'w') as f:
            f.write(inventory)

    def update_hadoop_setup_inventory(self):
        inventory_path = os.path.join('ansible', 'hadoop_setup', 'inventory')
        with open(os.path.join(inventory_path, 'inventory_template'), 'r') as f:
            template = Template(f.read())

        ip_entries = self.stack_info.get(HADOOP_DATANODE_PRIVATE_KEY).get('output_value')
        host_entries = []
        nodes = []
        for ip_entry in ip_entries:
            ip_address = ip_entry[0]
            host_entry = HOST_TEMPLATE.substitute(
                ipaddress=ip_address,
                ssh_user=ANSIBLE_SSH_USER,
                private_key_file=ANSIBLE_SSH_PRIVATE_KEY_FILE
            )
            host_entries.append(host_entry)
            nodes.append({'hostname': ip_entry[1], 'ip': ip_entry[0]})

        host_entries = '\n'.join(host_entries)
        inventory = template.substitute(node_hosts=host_entries)

        with open(os.path.join(inventory_path, 'hosts'), 'w') as f:
            f.write(inventory)

        nodes = {'nodes': nodes}
        with open(os.path.join(inventory_path, 'nodes'), 'w') as f:
            f.write(yaml.safe_dump(nodes, explicit_start=True, default_flow_style=False))

def main():
    syncer = InventorySyncer()
    syncer.update_master_setup_inventory()
    syncer.update_hadoop_setup_inventory()

if __name__ == '__main__':
    main()
