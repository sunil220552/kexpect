import re
import sys
import time
import os
import shutil

from kubernetes.client.exceptions import ApiException
from kubernetes.stream import stream

from .exceptions import TIMEOUT, ExceptionK8sAPI, ExceptionKexpect
from .k8s_client import k8sClient

class podsList:
    def __init__(self, container_info, base_path, healthy=False, unhealthy=False):
        self._container = container_info
        self._list_only_healthy = healthy
        self._list_only_unhealthy = unhealthy
        self._base_path = base_path
        self._list = []
        try:
            self._client = k8sClient().get_client()
        except ExceptionK8sAPI as exp:
            raise exp

    def pods_list(self):
        try:
            pod_list = self._client.list_namespaced_pod(self._container.namespace)
        except ApiException as e:
            msg = F"Exception when calling CoreV1Api->list_namespaced_pods: {e}"
            raise ApiException(msg)

        # below code for getting the pod list
        for pod in pod_list.items:
            # ignore the pods of other container(pool)
            if self._container.container_name != None and self._container.container_name != pod.status.container_statuses[0].name:               
                continue
            # Ignore unhealthy pods if healthy=True
            if self._list_only_healthy and pod.status.phase != "Running":
                continue
            # Ignore healthy pods if unhealthy=True
            if self._list_only_unhealthy and pod.status.phase == "Running":
                continue
            self._list.append(pod.metadata.name)
        print(F"\n pods list : {self._list}")
        return self._list

    def create_pod_dirs(self):
        # Create base directory based on namespace
        namespace_dir = os.path.join(self._base_path, self._container.namespace)
        if os.path.exists(namespace_dir):
            try:
                shutil.rmtree(namespace_dir, ignore_errors=False, onerror=None)
            except:
                print('Error while deleting directory')
        print(F"\nBuilding inventory at {namespace_dir}")
        # Pool directory
        service_dir = os.path.join(namespace_dir, self._container.container_name)
        pods_list = self.pods_list()
        if len(pods_list) == 0:
            print("Failed to build inventory. Please check the pods_list.")
        for pod in pods_list:
            pod_dir = os.path.join(service_dir, pod)
            print(F"\npod dir: {pod_dir}")
            os.makedirs(pod_dir)
        # create shell and prompt directory for the service
        with open(service_dir+"/shell", 'w') as f:
            f.write(self._container.shell)
        with open(service_dir+"/prompt", 'w') as f:
            f.write(self._container.prompt)
