import os
import json

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
    return(os.path.abspath(key_path))

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
