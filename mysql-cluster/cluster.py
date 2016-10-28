#!/usr/bin/python
#
# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#

import argparse
import datetime
import os
import platform
import shutil
import subprocess
import sys

REPO = "markleith/mysql-cluster"
VERSION = "7.5"

NAME = "mycluster"
BASE_NETWORK = "172.18"

NDBD = "ndbmtd"
NDBD_BASE_IMAGE = REPO+"-"+NDBD
NDBD_BASE_ID = 1

MGMD = "mgmd"
MGMD_BASE_IMAGE = REPO+"-"+MGMD
MGMD_BASE_ID = 49

API = "sql"
API_BASE_IMAGE = REPO+"-"+API
API_BASE_ID = 51

QUOTE = "\"" if platform.system() == "Windows" else "'"

CONFIG_INI = os.getcwd()+"/management-node/config.ini"

nodes=[]

class Node:
	def __init__(self, name, port, node_type):
		self.name = name
		self.port = port
		self.node_type = node_type

	def __str__(self):
		return(' "node" : { "name" : "'+str(self.name)+'", "bound_port" : '+str(self.port)+', "node_type" : "'+str(self.node_type)+'" } ')

	def __repr__(self):
		return str(self)

def add_node(nodeName, node_type):
	if node_type == MGMD:
		port = cmd("docker port {0} 1186/tcp".format(nodeName))
	elif node_type == NDBD:
		port = cmd("docker port {0} 11860/tcp".format(nodeName))
	elif node_type == API:
		port = cmd("docker port {0} 3306/tcp".format(nodeName))
	node = Node(nodeName, port.strip().split(":",1)[1], node_type)
	nodes.append(node)
	debug("Added: {0}".format(node))

def ts():
	return datetime.datetime.utcnow().isoformat()+": "

def log(msg):
	print ts()+msg

def debug(msg):
	if args.debug: print "{0}Debug: {1}".format(ts(), msg)

def cmd(cmd):
	log("Running: " + cmd)
	return subprocess.check_output(cmd, shell=True)

def ip(nodeid):
	return "{0}.0.1{1}".format(args.base_network, nodeid)

def node_name(nodeid, node_type):
	return "{0}-{1}{2}".format(args.name, node_type, nodeid)

def write_ini_section(file, header, nodeid):
	file.write("\n["+header+"]\n")
	file.write("NodeId={0}\n".format(nodeid))
	file.write("HostName={0}\n".format(ip(nodeid)))

def build_config_ini():
	try:
		cfgtmpl = os.getcwd()+"/management-node/config.ini.in"
		shutil.copy(cfgtmpl, CONFIG_INI)
	except shutil.Error as e:
		print('Error: %s' % e)
	except IOError as e:
		print('Error: %s' % e.strerror)
	with open(CONFIG_INI, "ab") as f:
		nodeid = MGMD_BASE_ID
		for i in range(args.management_nodes):
			write_ini_section(f, "NDB_MGMD", nodeid)
			nodeid += 1
		nodeid = NDBD_BASE_ID
		for i in range(args.data_nodes):
			write_ini_section(f, "NDBD", nodeid)
			nodeid += 1
		nodeid = API_BASE_ID
		for i in range(args.sql_nodes):
			write_ini_section(f, "MYSQLD", nodeid)
			nodeid += 1

def build(args):
	build_config_ini()
	cmd('docker build -t {0}:{1} -f management-node/Dockerfile management-node'.format(MGMD_BASE_IMAGE, VERSION))
	cmd('docker build -t {0}:{1} -f data-node/Dockerfile data-node'.format(NDBD_BASE_IMAGE, VERSION))
	cmd('docker build -t {0}:{1} -f sql-node/Dockerfile sql-node'.format(API_BASE_IMAGE, VERSION))

def get_container(name):
	container = cmd('docker ps -q -a --filter {0}name={1}{0}'.format(QUOTE, name)).rstrip(",\n")
	debug("Found container id {0}".format(container))
	if len(container) and container != "":
		return container
	else:
		return None

def network_exists(network):
	networks = cmd("docker network ls")
	if networks.find(network) != -1:
		return True
	else:
		return False

def connected_containers(network):
	containers = cmd(
		'docker network inspect --format={0}{{{{range $i, $c := .Containers}}}}{{{{$i}}}},{{{{end}}}}{0} {1}'.format(QUOTE, network)
	).rstrip(",\n").split(',')
	containers = [x[0:12] for x in containers]
	return containers

def connected_networks(container):
	return cmd(
		'docker inspect --format {0}{{{{range $i, $n := .NetworkSettings.Networks}}}}{{{{$i}}}},{{{{end}}}}{0} {1}'.format(QUOTE, container)
	).rstrip(",\n").split(',')

def start_container(container, expectedNetwork, name):
	networks = connected_networks(container)
	debug("Container {0} connected to networks {1}".format(container, " ".join(networks)))
	if any(expectedNetwork in n for n in networks):
		cmd("docker start {0}".format(container))
	else:
		log("Error: Found container {0}, but it wasn't part of the {1} network (it was on {2}), stopping!".format(name, args.name, ",".join(networks)))
		sys.exit()

def connect_string():
	mgmd_nodes = filter(lambda x: x.node_type == MGMD, nodes)
	return ",".join(x.name + ":1186" for x in mgmd_nodes)

def management_nodes_option(x):
	x = int(x)
	if x > 2:
		raise argparse.ArgumentTypeError("Maximum Managment nodes is 2")
	return x

def run_mgmd_nodes():
	nodeid = MGMD_BASE_ID
	mgmdSibling = nodeid + 1
	for i in range(args.management_nodes):
		if i: nodeid, mgmdSibling = mgmdSibling, nodeid
		nodeName = node_name(nodeid, MGMD)
		container = get_container(nodeName)
		if container is not None:
			start_container(container, args.name, nodeName)
		else:
			runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e NOWAIT={4} -e CONNECTSTRING={5} {6}:{7}'
			cmd(runCmd.format(args.name, nodeName, ip(nodeid), nodeid, mgmdSibling, connect_string(), MGMD_BASE_IMAGE, VERSION))
		add_node(nodeName, MGMD)

def data_nodes_option(x):
	x = int(x)
	if x > 48:
		raise argparse.ArgumentTypeError("Maximum Data nodes is 48")
	return x

def run_data_nodes():
	nodeid = NDBD_BASE_ID
	for i in range(args.data_nodes):
		nodeName = node_name(nodeid, NDBD)
		container = get_container(nodeName)
		if container is not None:
			start_container(container, args.name, nodeName)
		else:
			runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e CONNECTSTRING={4} {5}:{6}'
			cmd(runCmd.format(args.name, nodeName, ip(nodeid), nodeid, connect_string(), NDBD_BASE_IMAGE, VERSION))
		add_node(nodeName, NDBD)
		nodeid += 1

def run_sql_nodes():
	nodeid = API_BASE_ID
	for i in range(args.sql_nodes):
		nodeName = node_name(nodeid, API)
		container = get_container(nodeName)
		if container is not None:
			start_container(container, args.name, nodeName)
		else:
			runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e CONNECTSTRING={4} {5}:{6}'
			cmd(runCmd.format(args.name, nodeName, ip(nodeid), nodeid, connect_string(), API_BASE_IMAGE, VERSION))
		add_node(nodeName, API)
		nodeid += 1

def start(args):
	if not os.path.isfile(CONFIG_INI):
		log("Error: management-node/config.ini does not exist, you need to issue the build command first")
		sys.exit()
	if network_exists(args.name):
		log("Info: {0} network found, checking if any containers are already running".format(args.name))
		containers = connected_containers(args.name)
		if len(containers) and containers[0] != "":
			log("Error: {0} network already has running containers, please fully stop this cluster, or clean, before attempting to start".format(args.name))
			sys.exit()
	else:
		log("Info: {0} network not found, creating".format(args.name))
		cmd("docker network create --subnet=" + args.base_network + ".0.0/16 " + args.name)
	run_mgmd_nodes()
	run_data_nodes()
	run_sql_nodes()
	log("Info: Started: {0}".format(nodes))

def stop_containers(containers):
	cmd("docker stop {0}".format(" ".join(containers)))

def stop(args):
	if network_exists(args.name):
		debug("Found network {0}".format(args.name))
		containers = connected_containers(args.name)
		debug("Found containers: {0}".format(containers))
		if len(containers) and containers[0] != "":
			stop_containers(containers)
			log("Info: Stopping containers done")
		else:
			log("Info: No containers found running on {0}".format(args.name))
	else:
		log("Info: {0} network not found".format(args.name))

def find_containers_using_image(name):
	containers = cmd(
		'docker ps -a --filter {0}ancestor={1}{0} --format {0}{{{{.ID}}}}{0}'.format(QUOTE, name)
	).rstrip("\n").split('\n')
	debug("Found containers: {0}".format(containers))
	return containers

def remove_containers(containers):
	cmd("docker rm {0}".format(" ".join(containers)))

def find_images(repo_base):
	images = cmd(
		'docker images {0}-* --format {1}{{{{.ID}}}}{1}'.format(repo_base, QUOTE)
	).rstrip("\n").split('\n')
	debug("Found images: {0}".format(images))
	return images

def find_dangling_images():
	images = cmd(
		'docker images --filter {0}dangling=true{0}  --format {0}{{{{.ID}}}}{0}'.format(QUOTE)
	).rstrip("\n").split('\n')
	debug("Found dangling images: {0}".format(images))
	return images

def remove_images(images):
	cmd("docker rmi {0}".format(" ".join(images)))

def remove_network(network):
	cmd("docker network rm {0}".format(network))

def clean(args):
	containers = []
	containers.extend(find_containers_using_image(MGMD_BASE_IMAGE+":"+VERSION))
	containers.extend(find_containers_using_image(NDBD_BASE_IMAGE+":"+VERSION))
	containers.extend(find_containers_using_image(API_BASE_IMAGE+":"+VERSION))
	debug("Found containers: {0}".format(containers))
	if len(containers) and containers[0] != "":
		stop_containers(containers)
		remove_containers(containers)
	if args.images:
		images = find_images(REPO)
		if len(images) and images[0] != "":
			log("Info: Removing {0}-* images".format(REPO))
			remove_images(images)
	if args.dangling:
		dangling = find_dangling_images()
		if len(dangling) and dangling[0] != "":
			log("Info: Removing dangling images")
			remove_images(dangling)
	if args.name:
		if network_exists(args.name):
			remove_network(args.name)
	if network_exists(NAME):
		remove_network(NAME)
	if os.path.isfile(CONFIG_INI):
		os.remove(CONFIG_INI)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Create a test MySQL Cluster deployment in docker")
	name = argparse.ArgumentParser(add_help=False)
	name.add_argument('-n', '--name', default=NAME, help='The prefix to use for managing the network and containers (default: '+NAME+')')
	base_network = argparse.ArgumentParser(add_help=False)
	base_network.add_argument('-b', '--base-network', default=BASE_NETWORK, help='The base IP network range (default: '+BASE_NETWORK+')')
	mgmd_nodes = argparse.ArgumentParser(add_help=False)
	mgmd_nodes.add_argument('-m', '--management-nodes', default=2, type=management_nodes_option, help='Number of Management nodes to run (default: 2; max: 2)')
	data_nodes = argparse.ArgumentParser(add_help=False)
	data_nodes.add_argument('-d', '--data-nodes', default=4, type=data_nodes_option, help='Number of NDB nodes to run (default: 4; max: 48)')
	sql_nodes = argparse.ArgumentParser(add_help=False)
	sql_nodes.add_argument('-s', '--sql-nodes', default=2, type=int, help='Number of SQL nodes to run (default: 2)')
	sp = parser.add_subparsers()
	sp_build = sp.add_parser('build', parents=[base_network, mgmd_nodes, data_nodes, sql_nodes], help='Build the cluster containers')
	sp_build.set_defaults(func=build)
	sp_start = sp.add_parser('start', parents=[name, base_network, mgmd_nodes, data_nodes, sql_nodes], help='Start up the cluster containers')
	sp_start.set_defaults(func=start)
	sp_stop = sp.add_parser('stop', parents=[name], help='Stop the cluster containers for the specified network')
	sp_stop.set_defaults(func=stop)
	sp_clean = sp.add_parser('clean', parents=[name], help='Stop and remove the cluster containers')
	sp_clean.add_argument('-i', '--images', default=False, action="store_true", help='Delete '+REPO+' docker images (default: false)')
	sp_clean.add_argument('-d', '--dangling', default=False, action="store_true", help='Delete dangling docker images (default: false)')
	sp_clean.set_defaults(func=clean)
	parser.add_argument('--debug', default=False, action="store_true", help='Whether to print debug info (default: false)')
	args = parser.parse_args()

	debug("Arguments: {0}".format(args))

	args.func(args)
