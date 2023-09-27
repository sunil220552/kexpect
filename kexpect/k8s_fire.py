import os
import sys
from kexpect.container_info import containerInfo
import threading
from kexpect.exceptions import ExceptionKexpect
from kexpect.k8s_execute import KExecute

class KFire:
    def __init__(self, level, script, cmd_args=None, timeout=300, pro_mode=False, batch_size=5):
        print("in __init__")
        self._level = level
        self._script = script
        self._cmd_args = cmd_args
        self._timeout = timeout
        self._pro_mode = pro_mode
        self._batch_size = batch_size
        self._containers = []
        self._current_batch = None
        self._batch_success = None
        self._batch_failure = None
        self._success = []
        self._failure = []
        self._logs = {}
        self._build_containers()
    
    def _build_containers(self):
        for root, dirs, files in os.walk(self._level):
            print(F"in _build_contianers: roots:{root}, dirs:{dirs}, files:{files}\n")
            if not dirs:
                print(F"in _build_contianers: no directory")
                ns, container, pod = root.split("/")
                print(F"in _build_contianers: ns:{ns}, container:{container}, pod:{pod}\n")
                container = container.split(".")[0]
                shell_file = F"{ns}/{container}/shell"
                prompt_file = F"{ns}/{container}/prompt"
                shell = None
                prompt = None
                if os.path.exists(shell_file):
                    with open(shell_file, "r") as f:
                        shell = f.read().strip()
                else:
                    raise ExceptionKexpect(F"Shell file {shell_file} does not exist. Please review the inventory.")
                
                if os.path.exists(prompt_file):
                    with open(prompt_file, "r") as f:
                        prompt = f.read().strip()
                else:
                    raise ExceptionKexpect(F"Prompt file {prompt_file} does not exist. Please review the inventory.")
                
                self._containers.append(containerInfo(pod=pod, container=container, namespace=ns, shell=shell, prompt=prompt))
                self._logs[F"{pod}"] = F"{root}/current"
        print(self._logs)

    
    def _get_next_batch(self):
        for i in range(0, len(self._containers), self._batch_size):
            yield self._containers[i:i + self._batch_size]

    def _log_pre_fire(self):
        print("Pre fire")
        for container in self._current_batch:
            print(container)
    
    def _log_post_fire(self):
        print("Post fire")
        
    def _fire(self, container):
        log_file = self._logs[F"{container.pod}"]
        print("Fire")
        print(container)
        print("Shell : ", container.shell)
        print("Prompt : ", container.prompt)
        print("Log file : ", log_file)
        print("Script : ", self._script)
        print("Cmd args : ", self._cmd_args)
        print("Timeout : ", self._timeout)
        # import pdb; pdb.set_trace()
        
        kexec = KExecute(container, self._script, logfile=log_file)
        kexec.execute()
        kexec.exit()
        #self._batch_success.append(container)

    def _litmus_test(self):
        container = self._containers.pop(0)
        print()
        print("Performing litmus test on container: ", container)
        print()
        th = threading.Thread(target=self._fire, args=(container,))
        th.start()
        th.join()
        with open(self._logs[container], 'r') as fd:
            print("***************** Log from %s *****************" % (container))
            print(fd.read())

        print()
        print("************ Does log looks good? **************")
        print()

        choice = input("""
            A: Abort
            C: I am good... Continue
            Please enter your choice: """)

        if choice in [ "A", "a"]:
            sys.exit()
        elif choice == ["C", "c"]:
            self._success.append(container)


    def fire(self):
        if len(self._containers) > 1 and not self._pro_mode:
            self._litmus_test()

        for batch in self._get_next_batch():
            self._current_batch = batch
            threads = []
            self._batch_success = []
            self._batch_failure = []

            self._log_pre_fire()

            for container in batch:
                tr = threading.Thread(target=self._fire, args=(container,))
                threads.append(tr)
                tr.start()

            for tr in threads:
                tr.join()

            self._success.extend(self._batch_success)
            self._failure.extend(self._batch_failure)

            print("Done") 
            self._log_post_fire()

if __name__ == "__main__":
    # Create a KFire object
    script = '/Users/meetshah/Documents/k8s_helper/kexpect/examples/sample_run.sh'
    kfire = KFire("sigpolicy", script, cmd_args="test", timeout=300, pro_mode=True, batch_size=3)
    kfire.fire()