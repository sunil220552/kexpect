class containerInfo:
    def __init__(self, pod, container, namespace, shell, prompt):
        self.pod = pod
        self.container_name = container
        self.namespace = namespace
        self.shell = shell
        self.prompt = prompt
        self._pod_ip = None
        self._start_time = None
        self._build = None

    def set_start_time(self, start_time):
        self._start_time = start_time

    def set_pod_ip(self, pod_ip):
        self._pod_ip = pod_ip

    def set_build(self, build):
        self._build = build

    def __str__(self):
        return F"{self.pod}/{self.container_name}"
