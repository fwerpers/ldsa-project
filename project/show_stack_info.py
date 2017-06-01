import subprocess
import utils

stack_name = utils.get_stack_name()

command_str = "openstack stack output show --all " + stack_name
subprocess.Popen(command_str, shell=True).wait()
