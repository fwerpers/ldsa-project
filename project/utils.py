import os

def get_stack_name():
    with open('stack_name', 'r') as f:
        stack_name = f.readline().strip()
    return(stack_name)

def get_heat_template_path():
    region_dir = os.environ['OS_REGION_NAME']
    template_path = os.path.join(region_dir, 'heat-hadoop-cluster.yaml')
    return(template_path)

def get_key_path():
    region_dir = os.environ['OS_REGION_NAME']
    key_path = os.path.join(region_dir, region_dir.lower() + '_key.pem')
    return(key_path)
