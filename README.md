# Kamatera Toolbox

[Kamatera Cloud](https://www.kamatera.com/express/compute/) 3rd Party Tools and Integrations

## Getting Kamatera API keys

All the 3rd party tools and integrations require Kamatera API keys.

You can get the keys from the [Kamatera Console](https://console.kamatera.com/) under API > Keys

## Apache Libcloud

[Libcloud](https://libcloud.readthedocs.io/en/latest/) is a Python library for interacting with 
many of the popular cloud service providers using a unified API.

Kamatera is supported out of the box in latest Libcloud version 3.0.0 (with support for Python3 only).

Alternatively, if you are using Python 2 with Libcloud version 2.8.2, it can be installed as a standalone module.

Documentation:

* [Installation of latest Libcloud](https://libcloud.readthedocs.io/en/latest/getting_started.html#installation-development-version)
* [Libcloud Kamatera compute driver](https://libcloud.readthedocs.io/en/latest/compute/drivers/kamatera.html)
* [Standalone module for Python2 / Libcloud version 2.8.2](https://github.com/Kamatera/libcloud-driver-kamatera/blob/master/README.md)

## Ansible

[Ansible](https://docs.ansible.com/ansible/latest/user_guide/) delivers simple IT automation that ends 
repetitive tasks and frees up DevOps teams for more strategic work.

Kamatera is supported in Ansible version 2.9 or higher via an Ansible Galaxy collection available at https://galaxy.ansible.com/kamatera/kamatera

Documentation:

* [Ansible Installation guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
* [Kamatera Ansible collection](https://github.com/Kamatera/ansible-collection-kamatera/blob/master/README.md)
* After the collection is installed, detailed documentation is available via ansible-doc:
  * `ansible-doc kamatera.kamatera.kamatera_compute`
  * `ansible-doc kamatera.kamatera.kamatera_compute_options`

## Salt

[Salt](https://docs.saltstack.com/en/latest/) is a configuration managemenet and remote execution system.

Kamatera is supported for Salt versions 2019.2.0 or higher via a standalone module.

Documentation:

* [Salt Cloud Kamatera module](https://github.com/Kamatera/salt-cloud-module-kamatera/blob/master/README.md)
* [Using Salt Cloud](https://docs.saltstack.com/en/latest/topics/cloud/index.html)

## Terraform

[Terraform](https://www.terraform.io/) is a tool for building, changing, and versioning infrastructure safely and efficiently.

Kamatera is supported for Terraform version 0.12 or higher via a provider binary.

Documentation:

* [Kamatera Terraform provider](https://github.com/Kamatera/terraform-provider-kamatera/blob/master/README.md)
* [Introduction to Terraform](https://www.terraform.io/intro/index.html)

## Support

If you have any request, comment or found a bug, please email us: devteam@kamatera.com
