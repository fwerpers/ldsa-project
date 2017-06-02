import subprocess
import json
import utils
import os
import sys

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


stack_name = utils.get_stack_name()

json_data = subprocess.Popen("openstack stack output show -f json --all " + stack_name, shell=True, stdout=subprocess.PIPE).stdout.read()
stack_info = parse_stack_info(json_data)

ip = stack_info.get('hadoop_master_public_ip').get('output_value')
#key_path = os.path.join(os.environ['HOME'],'Desktop','hadoop_rsa')
key_path = utils.get_key_path()
args = ['ssh', 'ubuntu@' + ip, '-i', key_path, 'python ansible/hadoop_setup/setup_hadoop.py']
print(args)
subprocess.call(args)
