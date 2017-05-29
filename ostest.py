#!/Users/FWerpers/.virtualenvs/openstack/bin/python

# Script for creating an Openstack instance

import os
from openstack import connection

IMAGE_NAME = 'Ubuntu 16.04 LTS (Xenial Xerus) - latest'
FLAVOR_NAME = 'ssc.small'
NETWORK_NAME = 'SNIC 2017/13-8 Internal IPv4 Network'

def create_connection():
    auth_args = {
        'auth_url': 'https://c3se.cloud.snic.se:5000/v3',
        'project_name': 'SNIC 2017/13-8',
        'user_domain_name': 'snic',
        'project_domain_name': 'snic',
        'username': 's8770',
        'password': os.environ['SNIC_PW']
    }

    conn = connection.Connection(**auth_args)
    #conn.authorize()
    return(conn)

def list_instances(conn):
    servers = [ server for server in conn.compute.servers() ]
    for server in servers:
        print(server.name)

def list_images(conn):
    images = [ image for image in conn.compute.images() ]
    for image in images:
        print(image.name)

def get_instance(conn, name):
    server = conn.compute.find_server(name)
    return(server)

def create_instance(conn, name):
    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)

    server = conn.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}]
    )
    #floating_ip = conn.network.find_available_ip()
    #conn.compute.add_floating_ip_to_server
    server = conn.compute.wait_for_server(server)
    return(server)

def delete_instance(conn, instance_name):
    server = conn.compute.find_server(instance_name)
    conn.compute.delete_server(server)

def main():
    conn = create_connection()
    #server = create_instance(conn, 'felker_python')
    #delete_instance(conn, 'felker_python')
    #help(conn.network)
    #help(conn.compute)

if __name__ == '__main__':
    main()
