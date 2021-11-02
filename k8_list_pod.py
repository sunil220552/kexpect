from kubernetes import client, config
import os
import shutil

class k8ListPod:
    def __init__(self, pod_name):
        self._pod_name = pod_name
        self._pods = []
        self._client = None
        self._client = self._get_client()

    
    def _get_client(self):
        if self._client:
            return self._client

        config.load_kube_config()
        v1 = client.CoreV1Api()
        return v1

    def _filter(self, pod):
        if pod.metadata.name == self._pod_name:
            return True
        return False

    def _list_and_filter(self):
        ret = self._client.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if self._filter(i):
                self._pods.append(i)

    def list(self, basepath='.'):
        self._list_and_filter()
        containers = []
        for i in self._pods:
            pod_path = os.path.join(basepath, i.metadata.name)
            if os.path.isdir(pod_path):
                shutil.rmtree(pod_path)
            os.mkdir(pod_path)

            print(pod_path)
            for j in i.spec.containers:
                container_path = os.path.join(pod_path, j.name)
                os.mkdir(container_path)
                print(container_path)

if __name__ == "__main__":
    pod_lister = k8ListPod(pod_name='myapp')
    pod_lister.list()