from kexpect.k8s_spawn import spawn
from kexpect.exceptions import TIMEOUT, ExceptionK8sAPI, ExceptionKexpect
from kexpect.container_info import containerInfo
from kexpect.pods_list import podsList
import uuid
import time
import sys
import os

class KExecute(spawn):
    def __init__(self, container_info, script, logfile=None, cmd_args=None, timeout=300):
        
        super().__init__(container_info)
        self._update_logfile(logfile)
        self._script = script
        self._cmd_args = cmd_args
        self._timeout = timeout
        # Create a temporary file on the container
        # File will have unique random name to avoid conflicts
        self._remote_script = self._create_unique_name()

    def _update_logfile(self, logfile):
        if logfile:
            # open the logfile
            try:
                self._logfile = open(logfile, 'w+')
            except Exception as exp:
                msg = F"Failed to open logfile: {exp}"
                raise ExceptionKexpect(msg)
        else:
            self._logfile = sys.stdout

    def _create_unique_name(self):
        return F"/tmp/kexecute{uuid.uuid4()}.sh"
    
    def _create_remote_script(self):
        # Read the script into a string
        script = None
        try:
            with open(self._script, 'r') as f:
                script = f.read()
        # Handle file IO exceptions
        except Exception as exp:
            msg = F"Failed to read script: {exp}"
            raise ExceptionKexpect(msg)
        
        # Create the script on the container
        # Write the script to the temporary file
        self.sendline(F"cat <<'EOF' >> {self._remote_script}\n{script}\nEOF")
        self.expect_shell_prompt(300)
        if self.get_exit_status() != 0:
            msg = F"Failed to create remote script: {self.get_exit_status()}"
            raise ExceptionKexpect(msg)
        
    def _execute_remote_script(self):
        # Execute the script on the container
        if self._cmd_args:
            self.sendline(F"bash {self._remote_script} {self._cmd_args}")
        else:
            self.sendline(F"bash {self._remote_script}")
        self.expect_shell_prompt(300)
        if self.get_exit_status() != 0:
            msg = F"Failed to execute remote script: {self.get_exit_status()}"
            raise ExceptionKexpect(msg)

    def _cleanup_remote_script(self):
        # Remove the temporary file
        self.sendline(F"rm -f {self._remote_script}")
        self.expect_shell_prompt(30)
        if self.get_exit_status() != 0:
            msg = F"Failed to remove remote script: {self.get_exit_status()}"
            raise ExceptionKexpect(msg)

    def execute(self):
        # crete the remote script
        self._create_remote_script()
        self._execute_remote_script()
        # self._cleanup_remote_script()

if __name__ == "__main__":
    container_info = containerInfo(pod='beaker-c8c56c864-bflqd', container='beaker', namespace='sigpolicy', shell='/bin/bash', prompt='#')
    pods_list = podsList(container_info, os.curdir)
    pods_list.create_pod_dirs()
    kexec = KExecute(container_info, "/Users/meetshah/Documents/k8s_helper/kexpect/examples/sample_run.sh", logfile='kexec.log')
    kexec.execute()