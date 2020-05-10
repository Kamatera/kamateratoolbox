# Kamatera Toolbox

[Kamatera Cloud](https://www.kamatera.com/express/compute/) 3rd Party Tools and Integrations

## Getting Kamatera API keys

All the 3rd party tools and integrations require Kamatera API keys.

You can get the keys from the [Kamatera Console](https://console.kamatera.com/) under API > Keys

## Apache Libcloud

[Libcloud](https://libcloud.readthedocs.io/en/latest/) is a Python library for interacting with 
many of the popular cloud service providers using a unified API.

Kamatera is supported in the latest development version (which is stable and safe to use).

Documentation:

* [Installation of Libcloud development version](https://libcloud.readthedocs.io/en/latest/getting_started.html#installation-development-version)
* [Libcloud Kamatera compute driver](https://libcloud.readthedocs.io/en/latest/compute/drivers/kamatera.html)

## Ansible

[Ansible](https://docs.ansible.com/ansible/latest/user_guide/) delivers simple IT automation that ends 
repetitive tasks and frees up DevOps teams for more strategic work.

The Kamatera Ansible collection requires Ansible version 2.9 or later, see [Ansible Installation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

Install the Kamatera collection with the following command:

```
ansible-galaxy collection install https://github.com/Kamatera/ansible-collection-kamatera/releases/download/0.0.1/kamatera-kamatera-0.0.1.tar.gz
```

Documentation for the modules is available via ansible-doc by running the following commands:

```
ansible-doc kamatera.kamatera.kamatera_compute
ansible-doc kamatera.kamatera.kamatera_compute_options
```

To use the collection, define the following environment variables:

```
export KAMATERA_API_CLIENT_ID=
export KAMATERA_API_SECRET=
```

Example playbooks:

* [Get available datacenters](https://github.com/Kamatera/ansible-collection-kamatera/blob/master/tests/compute_datacenters_playbook.yml)
* [Get server options](https://github.com/Kamatera/ansible-collection-kamatera/blob/master/tests/compute_options_playbook.yml)
* [Provision and manage servers](https://github.com/Kamatera/ansible-collection-kamatera/blob/master/tests/compute_playbook.yml)

## Salt

[Salt](https://docs.saltstack.com/en/latest/) is a configuration managemenet and remote execution system.

The Kamatera module is pending approval by Salt, until it's approved it can be installed using Python:

```
pip install --upgrade https://github.com/Kamatera/salt/archive/kamatera-cloud.zip
```

Documentation:

* [Using Salt Cloud](https://docs.saltstack.com/en/latest/topics/cloud/index.html)
* [Getting started with Kamatera for Salt Cloud](https://github.com/Kamatera/salt/blob/kamatera-cloud/doc/topics/cloud/kamatera.rst#getting-started-with-kamatera)
