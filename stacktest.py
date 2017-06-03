import os
from openstack import connection
import yaml
import json

def create_connection():
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

def main():
    conn = create_connection()
    #help(conn.network)
    #help(conn.orchestration)

    stack = conn.orchestration.get_stack('DontDeleteMyStackBro')

    heat_path = os.path.join('HPC2N', 'heat-hadoop-cluster.yaml')
    # with open(heat_path, 'r') as f:
    #     d = yaml.load(f)
    # print(d['resources'])
    #
    # print(type(d))
    # print(len(d.keys()))

    # template_json = json.dumps(d)
    # a = json.loads(template_json)
    # print(type(a))
    # print(len(a.keys()))
    # print(template_json)

    # with open(heat_path, 'r') as f:
    #     temp = f.read()
    #conn.orchestration.update_stack(stack, template=temp)

    # params = stack.parameters
    # print(params)

    heat_path2 = os.path.join('HPC2N', 'heat-datanode.yaml')
    with open(heat_path2, 'r') as f:
        temp = f.read()
    with open(heat_path, 'r') as f:
        temp2 = f.read()
    conn.orchestration.validate_template(template=temp)
    conn.orchestration.create_stack(template=temp2, name='kalle')

if __name__ == '__main__':
    main()
