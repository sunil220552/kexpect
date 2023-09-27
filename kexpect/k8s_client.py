from kubernetes import config, client
from kexpect.exceptions import ExceptionK8sAPI

class k8sClient:
    def __init__(self):
        self._client = None
        try:
            config.load_kube_config()
            self._client = client.CoreV1Api()
            # Retrieve the current context
            current_context = config.list_kube_config_contexts()[1].get('context')

            # Extract the cluster name from the current context
            cluster_name = current_context.get('cluster')
            print(F"\nCluster: {cluster_name}\n")
        except Exception as exp:
            msg = F"Failed to create k8s client: {exp}"
            raise ExceptionK8sAPI(msg)

    def get_client(self):
        return self._client
