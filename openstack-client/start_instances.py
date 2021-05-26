import time
import os
import sys
import random
import json
import re
import inspect
from os import environ as env

from novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session


config = {}
instances = {}
nova = None


def load_config():
    global config

    if not os.path.isfile('../.config.json'):
        print(
            ".config.json is needed at the root of the project, check .config.json.template")
        exit()

    with open('../.config.json') as json_file:
        config = json.load(json_file)['open_stack_instances']


def authenticate_user():
    global nova
    loader = loading.get_plugin_loader('password')

    auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                    username=env['OS_USERNAME'],
                                    password=env['OS_PASSWORD'],
                                    project_name=env['OS_PROJECT_NAME'],
                                    project_domain_id=env['OS_PROJECT_DOMAIN_ID'],
                                    user_domain_name=env['OS_USER_DOMAIN_NAME'])

    sess = session.Session(auth=auth)
    nova = client.Client('2.1', session=sess)
    print("user authorization completed.")


def build_instance(instance_name):
    global instances

    flavor = config['flavor']
    private_net = config['private_net']
    image_id = config['image_id']
    identifier = config['identifier']
    key_name = config['key_name']

    image = nova.glance.find_image(image_id)

    flavor = nova.flavors.find(name=flavor)

    if private_net is not None:
        net = nova.neutron.find_network(private_net)
        nics = [{'net-id': net.id}]
    else:
        sys.exit("private-net not defined.")

    cfg_file_path = os.getcwd()+'/cloud-cfg.txt'
    if os.path.isfile(cfg_file_path):
        userdata = open(cfg_file_path)
    else:
        sys.exit("cloud-cfg.txt is not in current working directory")

    secgroups = ['default']

    instance = nova.servers.create(name=f"{instance_name}_{identifier}", image=image, flavor=flavor,
                                   key_name=key_name, userdata=userdata, nics=nics, security_groups=secgroups)
    instances[instance_name] = instance
    print(f"Starting building instance {instance_name}")


def wait_for_instances_build():
    print("waiting for 10 seconds.. ")
    time.sleep(10)

    while True:
        instances_are_built_count = 0
        for instance_name, instance in instances.items():

            if instance.status == 'BUILD':
                print("Instance: "+instance_name+" is in " +
                      instance.status+" state, sleeping for 5 seconds more...")
                time.sleep(5)
                instances[instance_name] = nova.servers.get(instance.id)
            else:
                instances_are_built_count += 1

        if instances_are_built_count == len(instances):
            print("Finished building instances")
            break


def print_instance_ip(instance):
    ip_address = None
    private_net = config['private_net']

    for network in instance.networks[private_net]:
        if re.match('\d+\.\d+\.\d+\.\d+', network):
            ip_address = network
            break
    if ip_address is None:
        raise RuntimeError('No IP address assigned!')

    print("Instance: " + instance.name + " is in " +
          instance.status + " state" + " ip address: " + ip_address)


'''
    template example:

    [servers]
    prodserver ansible_host=192.168.2.206
    devserver ansible_host=192.168.2.148
    worker1 ansible_host=192.168.2.148

    [workers]
    worker1

    [prodserver]
    prodserver ansible_connection=ssh ansible_user=appuser

    [devserver]
    devserver ansible_connection=ssh ansible_user=appuser

    [worker1]
    worker1 ansible_connection=ssh ansible_user=appuser

'''


def write_ansible_hosts_file():
    private_net = config['private_net']
    file_content = \
        '''
    [all:vars]
    ansible_python_interpreter=/usr/bin/python3\n
 '''
    file_content += "[servers]\n"
    ip_address = None

    # create the hosts
    for name, instance in instances.items():
        for network in instance.networks[private_net]:
            if re.match('\d+\.\d+\.\d+\.\d+', network):
                ip_address = network

        # _ is removed, because ansible doesn't like the character
        file_content += f"{name.replace('_', '')} " \
            f"ansible_host={ip_address}\n"

    file_content += "\n"
    # workers group
    file_content += "[workers]\n"
    for name in instances.keys():
        name = name.replace('_', '')
        if name[:6] == 'worker':
            file_content += f"{name}\n"

    file_content += "\n"
    # host names
    for name in instances.keys():
        name = name.replace('_', '')
        file_content += f"[{name}]\n"
        file_content += f"{name} ansible_connection=ssh " \
            "ansible_user=appuser\n\n"

    with open('inventory.ini', 'w') as f:
        f.write(file_content)

    print("Created inventory file")


def main():
    load_config()
    authenticate_user()
    build_instance('prod_server')
    build_instance('dev_server')

    for i in range(config['number_of_workers']):
        build_instance(f"worker_{i}")

    wait_for_instances_build()

    for instance in instances.values():
        print_instance_ip(instance)

    write_ansible_hosts_file()


if __name__ == '__main__':
    main()
