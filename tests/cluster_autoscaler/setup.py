import os
import json
import secrets
import datetime
import subprocess
from dataclasses import dataclass

import dotenv


def main():
    dotenv.load_dotenv()
    kamatera_api_client_id = os.getenv("KAMATERA_API_CLIENT_ID")
    kamatera_api_secret = os.getenv("KAMATERA_API_SECRET")
    name_prefix = os.getenv("KTBCA_NAME_PREFIX")
    if name_prefix:
        existing_name_prefix = True
        print('Using existing name prefix from environment variable KTBCA_NAME_PREFIX')
    else:
        existing_name_prefix = False
        name_prefix = f'kca{datetime.datetime.now().strftime("%m%d")}{secrets.token_hex(2)}'
    datacenter_id = "US-NY2"
    ssh_pubkeys = subprocess.check_output(["ssh-add", "-L"]).decode().strip()
    tfdir = os.path.join(os.path.dirname(__file__), "..", "..", ".data", "cluster_autoscaler", name_prefix, "terraform")
    os.makedirs(tfdir, exist_ok=existing_name_prefix)
    print(f'name prefix: {name_prefix}')
    print(f'terraform dir: {tfdir}')
    if not existing_name_prefix:
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
    ssh_pubkeys_ini_encoded = ssh_pubkeys.strip().replace("\n", "\n   ")
    with open(os.path.join(tfdir, "02-k8s", "ktb.auto.tfvars.json"), "w") as f:
        f.write(json.dumps({
            "cluster_autoscaler_kamatera_api_client_id": kamatera_api_client_id,
            "cluster_autoscaler_kamatera_api_secret": kamatera_api_secret,
            "cluster_autoscaler_global_config": f'''
default-ssh-key = {ssh_pubkeys_ini_encoded}
''',
            "cluster_autoscaler_nodegroup_configs": {},
            "cluster_autoscaler_nodegroup_rke2_extra_config": {}
        }))
    subprocess.check_call(["terraform", "init"], cwd=os.path.join(tfdir, "01-rke2"))
    subprocess.check_call(["terraform", "apply", "-auto-approve"], cwd=os.path.join(tfdir, "01-rke2"))
    subprocess.check_call(["terraform", "init"], cwd=os.path.join(tfdir, "02-k8s"))
    subprocess.check_call(["terraform", "apply", "-auto-approve"], cwd=os.path.join(tfdir, "02-k8s"))


if __name__ == "__main__":
    main()
