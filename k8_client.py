from kubernetes import config, client

class k8Client:
    def __init__(self):
        self._client = None
        self._client = self._create_client()

    def _create_client(self):
        if self._client:
            return self._client

        config.load_kube_config()
        v1 = client.CoreV1Api()
        return v1 

    def get_client(self):
        return self._client