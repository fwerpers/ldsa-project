import subprocess
import utils

stack_name = utils.get_stack_name()
template_path = utils.get_heat_template_path()

command_str = "openstack stack update -t " + template_path + " " + stack_name
subprocess.Popen(command_str, shell=True).wait()
