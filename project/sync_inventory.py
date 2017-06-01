#-------------------------------------------------------------------------------
# Name:        heat_inventory
# Purpose:
#
# Author:      Daniel Watrous
#
# Created:     10/07/2015
# Copyright:   (c) HP 2015
#-------------------------------------------------------------------------------
#!/usr/bin/python

import json
from string import Template
from textwrap import dedent
import subprocess
import utils
import os

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

class heat_inventory:

    # output keys
    hadoop_master_public_key = "hadoop_master_public_ip"
    hadoop_master_private_key = "hadoop_master_private_ip"
    hadoop_datanode_public_key = "nodes_public_ips"
    hadoop_datanode_private_key = "nodes_private_ips"

    # template values
    ansible_ssh_user = "ubuntu"
    ansible_ssh_private_key_file = utils.get_key_path()

    # templates
    host_entry = Template('$ipaddress ansible_connection=ssh ansible_user=$ssh_user ansible_ssh_private_key_file=$private_key_file')
    hosts_output = Template("""[hadoop-master]
$master_host

[hadoop-data]
$node_hosts

[hadoop-master:vars]
nodesfile=$nodes_path
key_path=$key_path

[hadoop-data:vars]
nodesfile=$nodes_path""")

    node_entry = Template("""  - hostname: $hostname
    ip: $ipaddress""")
    nodes_section = Template("""---
nodes:
$nodes
    """)
    nodes_sshkeyscan = Template('ssh-keyscan -t rsa $ipaddress >> ~/.ssh/known_hosts')

    def __init__(self):
        self.load_heat_output()

    def load_heat_output(self):
        stack_name = utils.get_stack_name()
        json_data = subprocess.Popen("openstack stack output show -f json --all " + stack_name, shell=True, stdout=subprocess.PIPE).stdout.read()
        self.heat_output = parse_stack_info(json_data)

    def get_master_public_ip(self):
        return(self.heat_output.get(self.hadoop_master_public_key).get('output_value'))

    def get_master_private_ip(self):
        return(self.heat_output.get(self.hadoop_master_private_key).get('output_value'))

    def get_datanode_private_ips(self):
        ip_entries = self.heat_output.get(self.hadoop_datanode_private_key).get('output_value')
        ips = [entry[0] for entry in ip_entries]
        return(ips)

    # Ansible hosts file
    def get_host_entry(self, ipaddress):
        return self.host_entry.substitute(ipaddress=ipaddress, ssh_user=self.ansible_ssh_user, private_key_file=self.ansible_ssh_private_key_file)

    def get_hosts_output(self):
        master_host = self.get_host_entry(self.get_master_public_ip())
        node_hosts = [self.get_host_entry(ipaddress) for ipaddress in self.get_datanode_private_ips()]
        node_hosts = '\n'.join(node_hosts)
        nodes_path = os.path.abspath(os.path.join('ansible','inventory', 'nodes-pro'))
        key_path = utils.get_key_path()
        return dedent(self.hosts_output.substitute(master_host=master_host, nodes_path=nodes_path, node_hosts=node_hosts, key_path=key_path))

    # Ansible group_vars nodes
    def get_node_entry(self, hostname, ipaddress):
        return self.node_entry.substitute(hostname=hostname, ipaddress=ipaddress)

    def get_nodes_entries(self):
        nodes = []
        nodes.append(self.get_node_entry('hadoop-master', self.get_master_private_ip()))
        for node in self.get_datanode_private_ips():
            nodes.append(self.get_node_entry(node[1], node[0]))
        return "\n".join(nodes)

    def get_nodes_output(self):
        return self.nodes_section.substitute(nodes=self.get_nodes_entries())

    def get_node_keyscan_script(self):
        nodes = []
        nodes.append(self.nodes_sshkeyscan.substitute(ipaddress=self.get_master_public_ip()))
        return "\n".join(nodes)

def main():
    heat_inv = heat_inventory()
##    print "hadoop master public IP: " + heat_inv.get_master_public_ip()
##    print "hadoop master private IP: " + heat_inv.get_master_private_ip()
##    print "hadoop datanode private IP: " + ', '.join(heat_inv.get_datanode_private_ips())
##    print "hadoop datanode public IP: " + ', '.join(heat_inv.get_datanode_public_ips())
    inventory_path = os.path.join('ansible','inventory')
    inventory_file = open(os.path.join(inventory_path, 'hosts-pro'), 'w')
    nodes_file = open(os.path.join(inventory_path, 'nodes-pro'), 'w')
    inventory_file.write(heat_inv.get_hosts_output())
    nodes_file.write(heat_inv.get_nodes_output())
    inventory_file.close()
    nodes_file.close()
    # keyscan_script_file = open('scan-node-keys.sh', 'w')
    # keyscan_script_file.write(heat_inv.get_node_keyscan_script())
    # keyscan_script_file.close()

if __name__ == '__main__':
    main()
