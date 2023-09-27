import re
import sys
import time
import os
import shutil

from kubernetes.client.exceptions import ApiException
from kubernetes.stream import stream

from .exceptions import TIMEOUT, ExceptionK8sAPI, ExceptionKexpect
from .k8s_client import k8sClient

class spawn():
    def __init__(self, container_info, logfile=sys.stdout):
        self._container = container_info
        self._session = None
        self._logfile = logfile
        self._prompt_re = re.compile(self._container.prompt)
        try:
            self._client = k8sClient().get_client()
        except ExceptionK8sAPI as exp:
            raise exp
        self._spawn()
        prompt_found, stdout, _ = self._expect_shell_prompt(10, loging=False)
        if not prompt_found:
            msg = F"Failed to login to {self._container} : {stdout}"
            raise ExceptionKexpect(msg)

    def _spawn(self):
        try:
            self._session = stream(self._client.connect_get_namespaced_pod_exec,
                  self._container.pod,
                  self._container.namespace,
                  container=self._container.container_name,
                  command=[self._container.shell],
                  stderr=True, stdin=True,
                  stdout=True, tty=True,
                  _preload_content=False)
        except ApiException as exp:
            msg = "Failed to login to {self._container} : {exp}"
            raise ExceptionK8sAPI(str(msg))

        if not self._session.is_open():
            msg = F"Failed to login to {self._container}"
            raise ExceptionKexpect(msg)

    def _log(self, out_str):
        try:
            self._logfile.write(out_str)
        except Exception as exp:
            msg = F"Failed to log: {exp}"
            raise ExceptionKexpect(msg)

    def _expect_shell_prompt(self, timeout, loging=True):
        start = time.time()
        stdout = ''
        stderr = ''
        prompt_found = False
        while time.time() - start < timeout:
            self._session.run_forever(timeout/100)
            if self._session.peek_stderr():
                tmp = self._session.read_stderr()
                stderr += tmp
                if loging:
                    self._log(tmp)
            if self._session.peek_stdout():
                tmp = self._session.read_stdout()
                if loging:
                    self._log(tmp)
                stdout += tmp
                if self._prompt_re.search(stdout):
                    prompt_found = True
                    break
            # Revisit to understand if '\n' can be avoided.
            self._session.write_stdin('\n')
        return (prompt_found, stdout, stderr)

    def expect_shell_prompt(self, timeout):
        prompt_found, _, _ = self._expect_shell_prompt(timeout)
        if not prompt_found:
            msg = F"Failed to complete the execution of the command in {timeout} seconds"
            raise TIMEOUT(msg)

    def get_exit_status(self):
        self.sendline('echo $?')
        prompt_found, stdout, _ = self._expect_shell_prompt(10)
        if not prompt_found:
            raise ExceptionKexpect("Failed to get exit status")
        ret_code = re.findall(r'(\d+)\r\n', stdout)
        if not ret_code or len(ret_code) > 1 or not ret_code[0].isdigit():
            raise ExceptionKexpect("Failed to get exit status")
        return int(ret_code[0])

    def sendline(self, cmd):
        self._session.write_stdin(cmd+'\n')

    def exit(self):
        self._session.close()
