# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys
from datetime import datetime
import inspect
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

flavor = "ACCHT18.normal" 
private_net = "SNIC 2019/10-32 Internal IPv4 Network"
floating_ip_pool_name = None
floating_ip = None
image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"
instance_name = "tisv1227-ubuntu16-" + datetime.now().strftime(datetime.now().strftime("d%y%m%dt%H%M%S"))

loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(
    auth_url=env['OS_AUTH_URL'],
    username=env['OS_USERNAME'],
    password=env['OS_PASSWORD'],
    project_name=env['OS_PROJECT_NAME'],
    project_domain_name=env['OS_USER_DOMAIN_NAME'],
    project_id=env['OS_PROJECT_ID'],
    user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print("user authorization completed.")

image = nova.glance.find_image(image_name)

flavor = nova.flavors.find(name=flavor)

if private_net != None:
    net = nova.neutron.find_network(name=private_net)
    nics = [{'net-id': net.id}]
else:
    sys.exit("private-net not defined.")

#print("Path at terminal when executing this file")
#print(os.getcwd() + "\n")
cfg_file_path =  os.getcwd()+'/cloud-cfg-simple.txt'
if os.path.isfile(cfg_file_path):
    userdata = open(cfg_file_path)
else:
    sys.exit("cloud-cfg.txt is not in current working directory")

    
secgroups = ['default', 'tisv1227']

print("Creating instance ... ")
instance = nova.servers.create(
    name=instance_name,
    image=image,
    flavor=flavor,
    userdata=userdata,
    nics=nics,
    security_groups=secgroups)

inst_status = instance.status
print("waiting for 10 seconds.. ")
time.sleep(10)

while inst_status == 'BUILD':
    print(
        "Instance: "+instance.name+" is in "+inst_status+
        " state, sleeping for 5 seconds more...")
    time.sleep(5)
    instance = nova.servers.get(instance.id)
    inst_status = instance.status

print("Instance: "+ instance.name +" is in " + inst_status + " state")
