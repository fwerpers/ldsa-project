import os
from openstack import connection

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
    a = conn.orchestration.get_stack('DontDeleteMyStackBro')
    b = conn.orchestration.check_stack(a)
    d = {'hej':'asd', 'botte':4, 'das':5}
    conn.orchestration.update_stack(a, template_file='project/HPC2N/heat-hadoop-cluster.yaml')
    #help(conn.orchestration.update_stack)

if __name__ == '__main__':
    main()
