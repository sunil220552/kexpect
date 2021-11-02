
from k8_client import k8Client

import time

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

class k8Exec:
    def __init__(self, pod_name, cont_name, script, shell, namespace='default'):
        self._pod_name = pod_name
        self._cont_name = cont_name
        self._namespace = namespace
        self._script = script
        self._shell = shell
        self._client = k8Client().get_client()
        self._session = None


    def _generate_session(self):
        if self._session:
            return

        #exec_command = [self._shell]
        exec_command = [
            '/bin/sh',
            '-c',
            'sleep 10; echo $?; echo done']

        self._session = stream(self._client.connect_get_namespaced_pod_exec,
                self._pod_name,
                self._namespace,
                container=self._cont_name,
                command=exec_command,
                stderr=True, stdin=True,
                stdout=True, tty=False)
        
        print("Response: " + self._session)
        
        #return self._session.is_open()

    def _copy_script(self):
        pass 

    def _execute_script(self):
        self._session.write_stdin("sleep 1; echo done\n")
        print("Response: " + self._session)
        # sdate = self._session.readline_stdout(timeout=3)
        # print("Server date command returns: %s" % sdate)
        # while self._session.is_open():
        #    pass
    
    def _close_session(self):
        self._session.close()

    def _cleanup(self):
        pass

    def _collect_status(self):
        pass 

    def execute(self):
        if not self._generate_session():
            print("Failed to generate session")
            return False

        # self._copy_script()

        # self._execute_script()

        # self._collect_status()

        # self._cleanup()

        # self._close_session()
        

if __name__ == "__main__":
    pod="myapp"
    cont_name="prometheus"
    script="test.sh"
    shell="/bin/sh"
    k8_exec = k8Exec(pod, cont_name, script, shell)
    k8_exec.execute()
    
        

    