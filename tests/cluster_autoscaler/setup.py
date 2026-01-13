import sys
import datetime
import json
import os
import secrets
import shutil
import subprocess

import dotenv


def load_json_env(var_name):
    value = os.getenv(var_name)
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise Exception(f"{var_name} must be valid JSON: {exc}") from exc


def write_k8s_vars(name_prefix, kamatera_api_client_id, kamatera_api_secret, ssh_pubkeys=None):
    if not ssh_pubkeys:
        ssh_pubkeys = subprocess.check_output(["bash", "-c", "cat ~/.ssh/*.pub"]).decode().strip()
    tfdir = str(os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler", name_prefix, "terraform"))
    ssh_pubkeys_ini_encoded = ssh_pubkeys.strip().replace("\n", "\\n")
    with open(os.path.join(tfdir, "02-k8s", "ktb.auto.tfvars.json"), "w") as f:
        f.write(json.dumps({
            "cluster_autoscaler_kamatera_api_client_id": kamatera_api_client_id,
            "cluster_autoscaler_kamatera_api_secret": kamatera_api_secret,
            "cluster_autoscaler_image": "ghcr.io/kamatera/kubernetes-autoscaler:v1.32-with-node-template-labels",
            "cluster_autoscaler_global_config": f'''
    default-ssh-key="{ssh_pubkeys_ini_encoded}"
    ''',

            "cluster_autoscaler_nodegroup_configs": {},
            "cluster_autoscaler_nodegroup_rke2_extra_config": {}
        }))


def run_setup(
    kamatera_api_client_id,
    kamatera_api_secret,
    name_prefix=None,
    datacenter_id="US-NY2",
    ssh_pubkeys=None,
):
    if name_prefix is None:
        name_prefix = f'kca{datetime.datetime.now().strftime("%m%d")}{secrets.token_hex(2)}'
    if ssh_pubkeys is None:
        ssh_pubkeys = subprocess.check_output(["bash", "-c", "cat ~/.ssh/*.pub"]).decode().strip()
    if not ssh_pubkeys:
        raise Exception("No SSH keys found in ssh-agent; run ssh-add")
    tfdir = os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler", name_prefix, "terraform")
    existing_name_prefix = (
        os.path.isdir(os.path.join(tfdir, "01-rke2"))
        and os.path.isdir(os.path.join(tfdir, "02-k8s"))
    )
    if existing_name_prefix:
        print("Using existing name prefix")
    os.makedirs(tfdir, exist_ok=True)
    print(f'name prefix: {name_prefix}')
    print(f'terraform dir: {tfdir}')
    if not existing_name_prefix:
        if os.listdir(tfdir):
            raise Exception(f"Terraform dir not empty at {tfdir}")
        subprocess.check_call([
            "git", "clone", "https://github.com/Kamatera/kamatera-rke2-kubernetes-terraform-example.git", ".",
            "--depth", "1"
        ], cwd=tfdir)
    with open(os.path.join(tfdir, "01-rke2", "ktb.auto.tfvars.json"), "w") as f:
        f.write(json.dumps({
            "kamatera_api_client_id": kamatera_api_client_id,
            "kamatera_api_secret": kamatera_api_secret,
            "datacenter_id": datacenter_id,
            "name_prefix": name_prefix,
            "ssh_pubkeys": ssh_pubkeys,
            "servers": {
                "default": {
                    "billing_cycle": "hourly",
                    "daily_backup": False,
                    "managed": False,
                    "cpu_type": "B",
                    "disk_sizes_gb": [100],
                },
                "bastion": {
                    "role": "bastion",
                    "cpu_cores": 1,
                    "ram_mb": 1024,
                    "disk_sizes_gb": [20],
                },
                "controlplane1": {
                    "role": "rke2",
                    "role_config": {
                        "rke2_type": "server",
                        "is_first_controlplane": True,
                    },
                    "cpu_cores": 4,
                    "ram_mb": 8192,
                }
            }
        }))
    write_k8s_vars(name_prefix, kamatera_api_client_id, kamatera_api_secret, ssh_pubkeys=ssh_pubkeys)
    subprocess.check_call(["terraform", "init"], cwd=os.path.join(tfdir, "01-rke2"))
    subprocess.check_call(["terraform", "apply", "-auto-approve"], cwd=os.path.join(tfdir, "01-rke2"))
    subprocess.check_call(["terraform", "init"], cwd=os.path.join(tfdir, "02-k8s"))
    subprocess.check_call(["terraform", "apply", "-auto-approve"], cwd=os.path.join(tfdir, "02-k8s"))
    return name_prefix


def destroy(name_prefix):
    tfdir = str(os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler", name_prefix, "terraform"))
    if os.path.isdir(os.path.join(tfdir, "02-k8s")):
        subprocess.check_call(["terraform", "destroy", "-auto-approve"], cwd=os.path.join(tfdir, "02-k8s"))
    if os.path.isdir(os.path.join(tfdir, "01-rke2")):
        subprocess.check_call(["terraform", "destroy", "-auto-approve"], cwd=os.path.join(tfdir, "01-rke2"))
    shutil.rmtree(os.path.join(tfdir, ".."), ignore_errors=True)
    kamatera_api_client_id = os.getenv("KAMATERA_API_CLIENT_ID")
    kamatera_api_secret = os.getenv("KAMATERA_API_SECRET")
    subprocess.check_call([
        "cloudcli",
        "--api-clientid", kamatera_api_client_id,
        "--api-secret", kamatera_api_secret,
        "server", "terminate", "--force", "--name", f'{name_prefix}.*'
    ])


def reset(name_prefix):
    kamatera_api_client_id = os.getenv("KAMATERA_API_CLIENT_ID")
    kamatera_api_secret = os.getenv("KAMATERA_API_SECRET")
    write_k8s_vars(name_prefix, kamatera_api_client_id, kamatera_api_secret)
    tfdir = str(os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler", name_prefix, "terraform"))
    subprocess.call([
        "kubectl", "delete", "ns", "ktbca-autoscaler-up-down"
    ], env={
        **os.environ,
        "KUBECONFIG": os.path.join(tfdir, ".kubeconfig"),
    })
    subprocess.check_call([
        "git", "pull", "origin", "main",
    ], cwd=tfdir)
    subprocess.check_call(["terraform", "init"], cwd=os.path.join(tfdir, "02-k8s"))
    subprocess.check_call(["terraform", "apply", "-auto-approve"], cwd=os.path.join(tfdir, "02-k8s"))
    subprocess.check_call([
        "cloudcli",
        "--api-clientid", kamatera_api_client_id,
        "--api-secret", kamatera_api_secret,
        "server", "terminate", "--force", "--name", f'{name_prefix}-autoscaler-.*'
    ])


def main(action='setup'):
    dotenv.load_dotenv()
    kamatera_api_client_id = os.getenv("KAMATERA_API_CLIENT_ID")
    kamatera_api_secret = os.getenv("KAMATERA_API_SECRET")
    if not kamatera_api_client_id or not kamatera_api_secret:
        raise Exception("KAMATERA_API_CLIENT_ID and KAMATERA_API_SECRET are required")
    name_prefix = os.getenv("KTBCA_NAME_PREFIX")
    if action == 'setup':
        run_setup(
            kamatera_api_client_id,
            kamatera_api_secret,
            name_prefix=name_prefix,
        )
    else:
        assert name_prefix, "KTBCA_NAME_PREFIX is not defined"
        if action == 'destroy':
            destroy(name_prefix)
        elif action == 'reset':
            reset(name_prefix)


if __name__ == "__main__":
    main(*sys.argv[1:])
