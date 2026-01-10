import datetime
import json
import os
import secrets
import subprocess
import sys
import time

import pytest


RUN_AUTOSCALER_TESTS = os.environ.get("KTBCA_RUN_AUTOSCALER_TESTS") == "yes"
POLL_SECONDS = 15
TIMEOUT_SECONDS = 900
NODEGROUP_NAME = "autoscaler"
NODEGROUP_MIN_SIZE = 1
NODEGROUP_MAX_SIZE = 3
NODEGROUP_CPU = "4B"
NODEGROUP_RAM_MB = 8192
NODEGROUP_DISK = "size=100"
NODE_LABEL_KEY = "role"
NODE_LABEL_VALUE = NODEGROUP_NAME
NODE_LABEL_SELECTOR = f"{NODE_LABEL_KEY}={NODE_LABEL_VALUE}"
WORKLOAD_REPLICAS = 3


def kubectl(kubeconfig_path, *args, input_text=None):
    result = subprocess.run(
        ["kubectl", "--kubeconfig", kubeconfig_path, *args],
        input=input_text,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout


def find_kubeconfig_path():
    data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler")
    )
    name_prefix = os.environ.get("KTBCA_NAME_PREFIX")
    if name_prefix:
        kubeconfig_path = os.path.join(data_dir, name_prefix, "terraform", ".kubeconfig")
        if os.path.exists(kubeconfig_path):
            return kubeconfig_path
        pytest.skip(f"kubeconfig not found at {kubeconfig_path}")
    if not os.path.isdir(data_dir):
        pytest.skip(f"cluster autoscaler data dir not found at {data_dir}")
    kubeconfigs = []
    for entry in os.listdir(data_dir):
        candidate = os.path.join(data_dir, entry, "terraform", ".kubeconfig")
        if os.path.exists(candidate):
            kubeconfigs.append(candidate)
    if not kubeconfigs:
        pytest.skip("no kubeconfig files found under cluster_autoscaler data dir")
    return max(kubeconfigs, key=os.path.getmtime)


def build_namespace_name():
    suffix = f"{datetime.datetime.now().strftime('%m%d%H%M%S')}{secrets.token_hex(2)}"
    return f"ktbca-{suffix}"[:63]


def build_name_prefix():
    suffix = f"{datetime.datetime.now().strftime('%m%d')}{secrets.token_hex(2)}"
    return f"kca{suffix}"


def build_nodegroup_configs():
    config_lines = [
        f"min-size={NODEGROUP_MIN_SIZE}",
        f"max-size={NODEGROUP_MAX_SIZE}",
        f"cpu={NODEGROUP_CPU}",
        f"ram={NODEGROUP_RAM_MB}",
        f"disk={NODEGROUP_DISK}",
        'template-label="kubernetes.io/os=linux"',
        f'template-label="{NODE_LABEL_KEY}={NODE_LABEL_VALUE}"',
    ]
    return {NODEGROUP_NAME: "\n".join(config_lines)}


def build_nodegroup_rke2_extra_config():
    return {
        NODEGROUP_NAME: f"""node-label:\n  - {NODE_LABEL_KEY}={NODE_LABEL_VALUE}\n"""
    }


def wait_for_condition(description, condition, timeout_seconds=TIMEOUT_SECONDS):
    start_time = time.time()
    while True:
        if condition():
            return
        if time.time() - start_time > timeout_seconds:
            raise AssertionError(f"timeout waiting for {description}")
        time.sleep(POLL_SECONDS)


def get_ready_node_count(kubeconfig_path, label_selector=None):
    args = ["get", "nodes"]
    if label_selector:
        args += ["-l", label_selector]
    args += ["-o", "json"]
    data = json.loads(kubectl(kubeconfig_path, *args))
    ready_nodes = 0
    for node in data.get("items", []):
        for condition in node.get("status", {}).get("conditions", []):
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                ready_nodes += 1
                break
    return ready_nodes


def get_pods(kubeconfig_path, namespace):
    data = json.loads(
        kubectl(kubeconfig_path, "get", "pods", "-n", namespace, "-o", "json")
    )
    return data.get("items", [])


def all_pods_running(kubeconfig_path, namespace, expected_replicas):
    pods = get_pods(kubeconfig_path, namespace)
    if len(pods) < expected_replicas:
        return False
    for pod in pods:
        if pod.get("status", {}).get("phase") != "Running":
            return False
    return True


def no_pods_exist(kubeconfig_path, namespace):
    return len(get_pods(kubeconfig_path, namespace)) == 0


def apply_deployment(kubeconfig_path, namespace, replicas):
    manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autoscaler-load
  namespace: {namespace}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: autoscaler-load
  template:
    metadata:
      labels:
        app: autoscaler-load
    spec:
      nodeSelector:
        {NODE_LABEL_KEY}: {NODE_LABEL_VALUE}
      containers:
      - name: load
        image: k8s.gcr.io/pause:3.9
        resources:
          requests:
            cpu: "2000m"
            memory: "1024Mi"
"""
    kubectl(kubeconfig_path, "apply", "-f", "-", input_text=manifest)


def scale_deployment(kubeconfig_path, namespace, replicas):
    kubectl(
        kubeconfig_path,
        "scale",
        "deployment/autoscaler-load",
        "-n",
        namespace,
        "--replicas",
        str(replicas),
    )


def delete_namespace(kubeconfig_path, namespace):
    subprocess.run(
        [
            "kubectl",
            "--kubeconfig",
            kubeconfig_path,
            "delete",
            "namespace",
            namespace,
            "--wait=false",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


@pytest.fixture(scope="session")
def autoscaler_cluster():
    name_prefix = os.environ.get("KTBCA_NAME_PREFIX")
    if not name_prefix:
        name_prefix = build_name_prefix()
        os.environ["KTBCA_NAME_PREFIX"] = name_prefix
    env = os.environ.copy()
    env["KTBCA_NAME_PREFIX"] = name_prefix
    env["KTBCA_NODEGROUP_CONFIGS_JSON"] = json.dumps(build_nodegroup_configs())
    env["KTBCA_NODEGROUP_RKE2_EXTRA_CONFIG_JSON"] = json.dumps(build_nodegroup_rke2_extra_config())
    setup_path = os.path.join(os.path.dirname(__file__), "setup.py")
    subprocess.check_call([sys.executable, setup_path], env=env)
    kubeconfig_path = find_kubeconfig_path()
    wait_for_condition(
        "autoscaler nodes to be ready",
        lambda: get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) >= NODEGROUP_MIN_SIZE,
    )
    return kubeconfig_path


@pytest.mark.skipif(
    not RUN_AUTOSCALER_TESTS, reason="set KTBCA_RUN_AUTOSCALER_TESTS=yes to run"
)
def test_autoscaler_scale_up(autoscaler_cluster):
    kubeconfig_path = autoscaler_cluster
    namespace = build_namespace_name()
    kubectl(kubeconfig_path, "create", "namespace", namespace)
    try:
        baseline_nodes = get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR)
        apply_deployment(kubeconfig_path, namespace, replicas=WORKLOAD_REPLICAS)
        wait_for_condition(
            "node count to increase",
            lambda: get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) > baseline_nodes,
        )
        wait_for_condition(
            "pods to be running",
            lambda: all_pods_running(
                kubeconfig_path, namespace, expected_replicas=WORKLOAD_REPLICAS
            ),
        )
    finally:
        delete_namespace(kubeconfig_path, namespace)


@pytest.mark.skipif(
    not RUN_AUTOSCALER_TESTS, reason="set KTBCA_RUN_AUTOSCALER_TESTS=yes to run"
)
def test_autoscaler_scale_down(autoscaler_cluster):
    kubeconfig_path = autoscaler_cluster
    namespace = build_namespace_name()
    kubectl(kubeconfig_path, "create", "namespace", namespace)
    try:
        baseline_nodes = get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR)
        apply_deployment(kubeconfig_path, namespace, replicas=WORKLOAD_REPLICAS)
        wait_for_condition(
            "node count to increase",
            lambda: get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) > baseline_nodes,
        )
        scaled_up_nodes = get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR)
        scale_deployment(kubeconfig_path, namespace, replicas=0)
        wait_for_condition(
            "pods to be deleted",
            lambda: no_pods_exist(kubeconfig_path, namespace),
        )
        wait_for_condition(
            "node count to decrease",
            lambda: get_ready_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) < scaled_up_nodes,
        )
    finally:
        delete_namespace(kubeconfig_path, namespace)
