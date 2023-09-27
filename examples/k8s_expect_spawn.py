"""
This script demonstrates how to use kexpect.spawn. 

Script logs into a container ( web ) of the pod : static-web and executes below command
* ls 
* pwd
The script will write stderr and stdout of the execution to stdout of the current shell. 
"""

from kexpect.k8s_spawn import spawn
from kexpect.container_info import containerInfo

if __name__ == "__main__":
    container_info = containerInfo(pod='beaker-84d48cc65d-dzxml', container='beaker', namespace='sigpolicy', shell='/bin/bash', prompt='#')
    tty_shell = spawn(container_info)
    print("Executing ls")
    tty_shell.sendline('ls')
    tty_shell.expect_shell_prompt(30)
    print(tty_shell.get_exit_status())
    print("Executing pwd")
    tty_shell.sendline('pwd')
    tty_shell.expect_shell_prompt(30)
    print(tty_shell.get_exit_status())
    print("Executing expr 1 + 1")
    tty_shell.sendline('expr 1 + 1')
    tty_shell.expect_shell_prompt(30)
    print(tty_shell.get_exit_status())
    tty_shell.exit()
