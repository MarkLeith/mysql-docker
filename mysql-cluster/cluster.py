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
import shutil
import subprocess

NDBD_BASE_ID = 1
NDBD_BASE_IP = "172.18.0.1"
MGMD_BASE_ID = 49
MGMD_BASE_IP = "172.18.0.2"
API_BASE_ID = 51
API_BASE_IP = "172.18.0.1"
SUBNET_BASE = "172.18.0.0/16"

nodes=[]

class Node:
	def __init__(self, name, port, node_type):
		self.name = name
		self.port = port
		self.node_type = node_type

	def __str__(self):
		return("Node("+str(self.name)+" : "+str(self.port)+" : "+str(self.node_type)+")")

	def __repr__(self):
		return str(self)

def add_node(nodeName, node_type):
	if node_type == "mgmd":
		port = cmd("docker port {0} 1186/tcp".format(nodeName))
	elif node_type == "ndbmtd":
		port = cmd("docker port {0} 11860/tcp".format(nodeName))
	elif node_type == "sql":
		port = cmd("docker port {0} 3306/tcp".format(nodeName))
	node = Node(nodeName, port.strip().split(":",1)[1], node_type)
	nodes.append(node)
	debug("Added: {0}".format(node))

def ts():
	return datetime.datetime.utcnow().isoformat()+": "

def debug(msg):
	if args.debug: print ts()+msg

def cmd(cmd):
	debug("Running: " + cmd)
	return subprocess.check_output(cmd, shell=True)

def write_ini_section(file, header, nodeid, nodeip):
	file.write("\n["+header+"]\n")
	file.write("NodeId={0}\n".format(nodeid))
	file.write("HostName={0}\n".format(nodeip))

def build_config_ini():
	config_ini = os.getcwd()+"/management-node/config.ini"
	try:
		cfgtmpl = os.getcwd()+"/management-node/config.ini.in"
		shutil.copy(cfgtmpl, config_ini)
	except shutil.Error as e:
		print('Error: %s' % e)
	except IOError as e:
		print('Error: %s' % e.strerror)
	with open(config_ini, "ab") as f:
		nodeid = MGMD_BASE_ID
		for i in range(args.management_nodes):
			write_ini_section(f, "NDB_MGMD", nodeid, "{0}{1}".format(MGMD_BASE_IP, nodeid))
			nodeid += 1
		nodeid = NDBD_BASE_ID
		for i in range(args.data_nodes):
			write_ini_section(f, "NDBD", nodeid, "{0}{1}".format(NDBD_BASE_IP, nodeid))
			nodeid += 1
		nodeid = API_BASE_ID
		for i in range(args.sql_nodes):
			write_ini_section(f, "MYSQLD", nodeid, "{0}{1}".format(API_BASE_IP, nodeid))
			nodeid += 1

def connect_string():
	mgmd_nodes = filter(lambda x: x.node_type == "mgmd", nodes)
	return ",".join(x.name+":1186" for x in mgmd_nodes)

def management_nodes_option(x):
	x = int(x)
	if x > 2:
		raise argparse.ArgumentTypeError("Maximum Managment nodes is 2")
	return x

def create_mgmd_nodes():
	nodeid = MGMD_BASE_ID
	mgmdSibling = nodeid + 1
	ndbConnectString = ""
	for i in range(args.management_nodes):
		if i: nodeid, mgmdSibling = mgmdSibling, nodeid
		nodeName = "mymgmd{0}".format(nodeid)
		ip = "{0}{1}".format(MGMD_BASE_IP, nodeid)
		runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e NOWAIT={4} -e CONNECTSTRING={5} markleith/mysqlcluster75:ndb_mgmd'
		cmd(runCmd.format(args.network, nodeName, ip, nodeid, mgmdSibling, connect_string()))
		add_node(nodeName, "mgmd")

def data_nodes_option(x):
	x = int(x)
	if x > 48:
		raise argparse.ArgumentTypeError("Maximum Data nodes is 48")
	return x

def create_data_nodes():
	nodeid = NDBD_BASE_ID
	for i in range(args.data_nodes):
		nodeName = "myndbmtd{0}".format(nodeid)
		ip = "{0}{1}".format(NDBD_BASE_IP, nodeid)
		runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e CONNECTSTRING={4} markleith/mysqlcluster75:ndbmtd'
		cmd(runCmd.format(args.network, nodeName, ip, nodeid, connect_string()))
		add_node(nodeName, "ndbmtd")
		nodeid += 1

def create_sql_nodes():
	nodeid = API_BASE_ID
	for i in range(args.sql_nodes):
		nodeName = "mysqlndb{0}".format(nodeid)
		ip = "{0}{1}".format(API_BASE_IP, nodeid)
		runCmd = 'docker run -d -P --net {0} --name {1} --ip {2} -e NODE_ID={3} -e CONNECTSTRING={4} markleith/mysqlcluster75:sql'
		cmd(runCmd.format(args.network, nodeName, ip, nodeid, connect_string()))
		add_node(nodeName, "sql")
		nodeid += 1

def build(args):
	build_config_ini()
	cmd('docker build -t markleith/mysqlcluster75:ndb_mgmd -f management-node/Dockerfile management-node')
	cmd('docker build -t markleith/mysqlcluster75:ndbmtd -f data-node/Dockerfile data-node')
	cmd('docker build -t markleith/mysqlcluster75:sql -f sql-node/Dockerfile sql-node')

def start(args):
	networks = cmd("docker network ls")
	if networks.find(args.network) != -1:
		debug(args.network + " network found, using existing")
	else:
		debug(args.network + " network not found, creating")
		cmd("docker network create --subnet="+SUBNET_BASE+" "+args.network)
	create_mgmd_nodes()
	create_data_nodes()
	create_sql_nodes()
	print "{0}Started: {1}".format(ts(), nodes)

def stop(args):
	debug("OH DEAR, MUST IMPLEMENT STOP")

def clean(args):
	debug("OH DEAR, MUST IMPLEMENT CLEAN")

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Create a test MySQL Cluster deployment in docker")
	network = argparse.ArgumentParser(add_help=False)
	network.add_argument('-n', '--network', default="myclusternet", help='Name of the docker network to use')
	mgmd_nodes = argparse.ArgumentParser(add_help=False)
	mgmd_nodes.add_argument('-m', '--management-nodes', default=2, type=management_nodes_option, help='Number of Management nodes to run (default: 2; max: 2)')
	data_nodes = argparse.ArgumentParser(add_help=False)
	data_nodes.add_argument('-d', '--data-nodes', default=4, type=data_nodes_option, help='Number of NDB nodes to run (default: 4; max: 48)')
	sql_nodes = argparse.ArgumentParser(add_help=False)
	sql_nodes.add_argument('-s', '--sql-nodes', default=2, type=int, help='Number of SQL nodes to run (default: 2)')
	sp = parser.add_subparsers()
	sp_build = sp.add_parser('build', parents=[mgmd_nodes, data_nodes, sql_nodes], help='Build the cluster containers')
	sp_build.set_defaults(func=build)
	sp_start = sp.add_parser('start', parents=[network, mgmd_nodes, data_nodes, sql_nodes], help='Start up the cluster containers')
	sp_start.set_defaults(func=start)
	sp_stop = sp.add_parser('stop', parents=[network], help='Stop the cluster containers')
	sp_stop.set_defaults(func=stop)
	sp_clean = sp.add_parser('clean', parents=[network], help='Stop and remove the cluster containers')
	sp_clean.set_defaults(func=clean)
	parser.add_argument('--debug', default=False, action="store_true", help='Whether to print debug info')
	args = parser.parse_args()

	debug("Arguments: {0}".format(args))

	args.func(args)
