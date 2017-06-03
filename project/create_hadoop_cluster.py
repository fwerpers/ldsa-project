import subprocess
import utils
from string import Template
import json
import os
import yaml
import paramiko
from openstack import connection
import time

HADOOP_MASTER_PUBLIC_KEY = "hadoop_master_public_ip"
HADOOP_MASTER_PRIVATE_KEY = "hadoop_master_private_ip"
HADOOP_DATANODE_PRIVATE_KEY = "nodes_private_ips"

ANSIBLE_SSH_USER = "ubuntu"
ANSIBLE_SSH_PRIVATE_KEY_FILE = "~/.ssh/hadoop_key.pem"
HOST_TEMPLATE = Template('$ipaddress ansible_connection=ssh ansible_user=$ssh_user ansible_ssh_private_key_file=$private_key_file')

# def source_credentials():
#     subprocess.Popen("source ", shell=True).wait()

def create_os_connection():
    auth_args = {
        'auth_url': os.environ['OS_AUTH_URL'],
        'project_name': os.environ['OS_PROJECT_NAME'],
        'user_domain_name': os.environ['OS_USER_DOMAIN_NAME'],
        'project_domain_name': os.environ['OS_USER_DOMAIN_NAME'],
        'username': os.environ['OS_USERNAME'],
        'password': os.environ['OS_PASSWORD']
    }

    conn = connection.Connection(**auth_args)
    #conn.authorize()
    return(conn)

def create_stack():
    stack_name = utils.get_stack_name()
    template_path = utils.get_heat_template_path()

    command_str = "openstack stack create --wait -t " + template_path + " " + stack_name
    subprocess.Popen(command_str, shell=True).wait()

    conn = create_os_connection()
    stack = conn.orchestration.get_stack(stack_name)
    if stack.status == 'CREATE_FAILED':
        raise RuntimeError('Stack creation failed.')

def get_stack_info(stack_name):
    stack_name = utils.get_stack_name()
    conn = create_os_connection()
    stack = conn.orchestration.get_stack(stack_name)

    stack_info = {}
    for item in stack.outputs:
        stack_info[item['output_key']] = item['output_value']
    return(stack_info)

class InventorySyncer:

    def __init__(self):
        self.stack_info = get_stack_info(utils.get_stack_name)
        self.replace_known_host()

    def replace_known_host(self):
        # Remove existing host key
        ip_address = self.stack_info.get(HADOOP_MASTER_PUBLIC_KEY)
        subprocess.Popen("ssh-keygen -R " + ip_address, shell=True).wait()

        # Add host key to prevent prompt
        ## Wait for public key
        while True:
            line = subprocess.Popen("ssh-keyscan -t rsa " + ip_address, shell=True, stdout=subprocess.PIPE).stdout.read()
            if line != '':
                break
        subprocess.Popen("ssh-keyscan -t rsa " + ip_address + " >> ~/.ssh/known_hosts", shell=True).wait()

    def update_master_setup_inventory(self):
        inventory_path = os.path.join('ansible', 'master_setup', 'inventory')
        with open(os.path.join(inventory_path, 'inventory_template'), 'r') as f:
            template = Template(f.read())

        # Hosts file
        ip_address = self.stack_info.get(HADOOP_MASTER_PUBLIC_KEY)
        key_path = utils.get_key_path()
        nodes_path = os.path.abspath(os.path.join(inventory_path, 'nodes'))
        host_entry = HOST_TEMPLATE.substitute(
            ipaddress=ip_address,
            ssh_user=ANSIBLE_SSH_USER,
            private_key_file=key_path
        )

        inventory = template.substitute(
            master_host=host_entry,
            key_path=key_path,
            nodes_path=nodes_path
        )

        with open(os.path.join(inventory_path, 'hosts'), 'w') as f:
            f.write(inventory)

        # Nodes files
        ip_entries = self.stack_info.get(HADOOP_DATANODE_PRIVATE_KEY)
        nodes = []
        master_private_ip = self.stack_info.get(HADOOP_MASTER_PRIVATE_KEY)
        nodes.append({'hostname': 'hadoop-master', 'ip': master_private_ip})
        for ip_entry in ip_entries:
            nodes.append({'hostname': ip_entry[1], 'ip': ip_entry[0]})
        nodes = {'nodes': nodes}
        with open(os.path.join(inventory_path, 'nodes'), 'w') as f:
            f.write(yaml.safe_dump(nodes, explicit_start=True, default_flow_style=False))

    def update_hadoop_setup_inventory(self):
        inventory_path = os.path.join('ansible', 'hadoop_setup', 'inventory')
        with open(os.path.join(inventory_path, 'inventory_template'), 'r') as f:
            template = Template(f.read())

        # Hosts file
        ip_entries = self.stack_info.get(HADOOP_DATANODE_PRIVATE_KEY)
        host_entries = []
        for ip_entry in ip_entries:
            ip_address = ip_entry[0]
            host_entry = HOST_TEMPLATE.substitute(
                ipaddress=ip_address,
                ssh_user=ANSIBLE_SSH_USER,
                private_key_file=ANSIBLE_SSH_PRIVATE_KEY_FILE
            )
            host_entries.append(host_entry)

        host_entries = '\n'.join(host_entries)
        nodes_path = os.path.abspath(os.path.join(inventory_path, 'nodes'))
        inventory = template.substitute(
            node_hosts=host_entries,
            nodes_path='inventory/nodes'
        )

        with open(os.path.join(inventory_path, 'hosts'), 'w') as f:
            f.write(inventory)

        # Nodes files
        nodes = []
        master_private_ip = self.stack_info.get(HADOOP_MASTER_PRIVATE_KEY)
        nodes.append({'hostname': 'hadoop-master', 'ip': master_private_ip})
        for ip_entry in ip_entries:
            nodes.append({'hostname': ip_entry[1], 'ip': ip_entry[0]})
        nodes = {'nodes': nodes}
        with open(os.path.join(inventory_path, 'nodes'), 'w') as f:
            f.write(yaml.safe_dump(nodes, explicit_start=True, default_flow_style=False))

        vars_path_master = os.path.join('ansible', 'hadoop_setup', 'roles', 'master', 'vars')
        with open(os.path.join(vars_path_master, 'nodes'), 'w') as f:
            f.write(yaml.safe_dump(nodes, explicit_start=True, default_flow_style=False))
        vars_path_common = os.path.join('ansible', 'hadoop_setup', 'roles', 'common', 'vars')
        with open(os.path.join(vars_path_common, 'nodes'), 'w') as f:
            f.write(yaml.safe_dump(nodes, explicit_start=True, default_flow_style=False))

def set_up_master():
    master_setup_path = os.path.join('ansible','master_setup')
    inventory_path = os.path.join(master_setup_path,'inventory', 'hosts')
    playbook_path = os.path.join(master_setup_path, 'playbook.yml')
    command_str = "ansible-playbook -i " + inventory_path + " " + playbook_path + " -v -c paramiko"
    subprocess.Popen(command_str, shell=True).wait()

def set_up_hadoop():
    conn = create_os_connection()
    stack = conn.orchestration.get_stack('DontDeleteMyStackBro')
    stack_info = get_stack_info(stack)
    ip = stack_info.get(HADOOP_MASTER_PUBLIC_KEY)
    key_path = utils.get_key_path()
    args = ['ssh', 'ubuntu@' + ip, '-i', key_path, 'python ansible/hadoop_setup/setup_hadoop.py']
    subprocess.call(args)

def start_hadoop():
    print('Starting Hadoop services')
    conn = create_os_connection()
    stack = conn.orchestration.get_stack('DontDeleteMyStackBro')
    stack_info = get_stack_info(stack)
    ip = stack_info.get(HADOOP_MASTER_PUBLIC_KEY)
    #key_path = utils.get_key_path()
    #key_path = os.path.join('ansible', 'hadoop_setup', 'roles', 'master', 'templates', 'hadoop_rsa')
    key_path = os.path.join(os.environ['HOME'], 'Desktop', 'hadoop_rsa')

    paramiko
    args = ['ssh', '-A', 'hadoop@' + ip, '-i', key_path, 'bash /home/ubuntu/ansible/hadoop_setup/start_hadoop.sh']
    subprocess.call(args)

def main():
    create_stack()
    syncer = InventorySyncer()
    syncer.update_master_setup_inventory()
    print('Updated inventory for master setup.')
    syncer.update_hadoop_setup_inventory()
    print('Updated inventory for hadoop setup.')
    set_up_master()
    set_up_hadoop()

    #start_hadoop()

if __name__ == '__main__':
    main()
