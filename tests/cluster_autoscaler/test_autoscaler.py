import datetime
import json
import os
import secrets
import subprocess
import time

import pytest
import dotenv


dotenv.load_dotenv()


RUN_AUTOSCALER_TESTS = os.environ.get("KTBCA_RUN_AUTOSCALER_TESTS") == "yes"
NAME_PREFIX = os.environ.get("KTBCA_NAME_PREFIX")
KEEP_CLUSTER = bool(NAME_PREFIX) or os.environ.get("KTBCA_KEEP_CLUSTER") == "yes"
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


def get_autoscaler_data_dir():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler")
    )


def find_kubeconfig_path(name_prefix=None):
    data_dir = get_autoscaler_data_dir()
    if not name_prefix:
        name_prefix = NAME_PREFIX
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
        pytest.skip("no kubeconfig files found under cluster autoscaler data dir")
    return max(kubeconfigs, key=os.path.getmtime)


def get_terraform_dir(name_prefix):
    return os.path.join(get_autoscaler_data_dir(), name_prefix, "terraform")


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


def load_tfvars(path):
    with open(path) as tfvars_file:
        return json.load(tfvars_file)


def write_tfvars(path, data):
    with open(path, "w") as tfvars_file:
        tfvars_file.write(json.dumps(data))


def add_autoscaler_nodegroup(terraform_dir):
    tfvars_path = os.path.join(terraform_dir, "02-k8s", "ktb.auto.tfvars.json")
    tfvars = load_tfvars(tfvars_path)
    tfvars["cluster_autoscaler_nodegroup_configs"] = build_nodegroup_configs()
    tfvars["cluster_autoscaler_nodegroup_rke2_extra_config"] = (
        build_nodegroup_rke2_extra_config()
    )
    write_tfvars(tfvars_path, tfvars)
    subprocess.check_call(
        ["terraform", "apply", "-auto-approve"],
        cwd=os.path.join(terraform_dir, "02-k8s"),
    )


def wait_for_condition(description, condition, timeout_seconds=TIMEOUT_SECONDS):
    start_time = time.time()
    while True:
        if condition():
            return
        if time.time() - start_time > timeout_seconds:
            raise AssertionError(f"timeout waiting for {description}")
        time.sleep(POLL_SECONDS)


def get_node_count(kubeconfig_path, label_selector=None):
    args = ["get", "nodes"]
    if label_selector:
        args += ["-l", label_selector]
    args += ["-o", "json"]
    data = json.loads(kubectl(kubeconfig_path, *args))
    total_nodes = 0
    ready_nodes = 0
    for node in data.get("items", []):
        total_nodes += 1
        for condition in node.get("status", {}).get("conditions", []):
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                ready_nodes += 1
                break
    return total_nodes, ready_nodes


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
        image: registry.k8s.io/pause:3.9
        resources:
          requests:
            cpu: "3000m"
            memory: "6000Mi"
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


@pytest.fixture()
def autoscaler_cluster():
    kamatera_api_client_id = os.getenv("KAMATERA_API_CLIENT_ID")
    kamatera_api_secret = os.getenv("KAMATERA_API_SECRET")
    name_prefix = NAME_PREFIX
    if name_prefix:
        kubeconfig_path = find_kubeconfig_path(name_prefix)
        assert get_node_count(kubeconfig_path) == (1, 1)
        yield name_prefix, kubeconfig_path
    else:
        from . import setup as autoscaler_setup

        name_prefix = autoscaler_setup.run_setup(
            kamatera_api_client_id,
            kamatera_api_secret,
            nodegroup_configs={},
            nodegroup_rke2_extra_config={},
        )
        try:
            kubeconfig_path = find_kubeconfig_path(name_prefix)
            wait_for_condition(
                "cluster should have a single controlplane node",
                lambda: get_node_count(kubeconfig_path) == (1, 1),
            )
            yield name_prefix, kubeconfig_path
        finally:
            if KEEP_CLUSTER:
                print(f"Keeping cluster with name prefix {name_prefix}")
            else:
                autoscaler_setup.destroy(name_prefix)


@pytest.mark.skipif(
    not RUN_AUTOSCALER_TESTS, reason="set KTBCA_RUN_AUTOSCALER_TESTS=yes to run"
)
def test_autoscaler_scale_up_down(autoscaler_cluster):
    name_prefix, kubeconfig_path = autoscaler_cluster
    print("Using cluster with name prefix:", name_prefix)
    print("Using kubeconfig path:", kubeconfig_path)
    terraform_dir = get_terraform_dir(name_prefix)
    namespace = "ktbca-autoscaler-up-down"
    kubectl(kubeconfig_path, "create", "namespace", namespace)
    try:
        wait_for_condition(
            "autoscaler baseline - single node",
            lambda: get_node_count(kubeconfig_path) == (1,1),
        )
        add_autoscaler_nodegroup(terraform_dir)
        apply_deployment(kubeconfig_path, namespace, replicas=1)
        wait_for_condition(
            "pods to be running",
            lambda: all_pods_running(
                kubeconfig_path, namespace, expected_replicas=1
            ),
        )
        wait_for_condition(
            "1 autoscaler node ready",
            lambda: get_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) == (1,1),
        )
        apply_deployment(kubeconfig_path, namespace, replicas=4)
        wait_for_condition(
            "pods to be running",
            lambda: all_pods_running(
                kubeconfig_path, namespace, expected_replicas=3
            ),
        )
        wait_for_condition(
            "3 autoscaler node ready",
            lambda: get_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) == (3, 3),
        )
        scale_deployment(kubeconfig_path, namespace, replicas=2)
        wait_for_condition(
            "pods to be running",
            lambda: all_pods_running(
                kubeconfig_path, namespace, expected_replicas=1
            ),
        )
        wait_for_condition(
            "node count down to 2",
            lambda: get_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) == (2,2),
        )
        scale_deployment(kubeconfig_path, namespace, replicas=0)
        wait_for_condition(
            "no pods",
            lambda: no_pods_exist(kubeconfig_path, namespace)
        )
        wait_for_condition(
            "node count down to 1",
            lambda: get_node_count(kubeconfig_path, NODE_LABEL_SELECTOR) == (1,1),
        )
    finally:
        if KEEP_CLUSTER:
            print(f"Keeping namespace {namespace}")
        else:
            delete_namespace(kubeconfig_path, namespace)
