mysql-docker
============

Docker configurations for running MySQL deployments.

## MySQL Flavors

All MySQL instances are configured to listen on port 3306 (the default), with the following users able to connect from all hosts:

* root / mysql (the default SUPER user)
* repl / repl (a replication user)
* mem / mem (a MySQL Enterprise Monitor user)

### mysql-cluster

Sets up a MySQL Cluster using the latest Oracle Linux and MySQL Cluster 7.5.4.

A wrapper script is included that allows you to build and start the cluster:

```
$ cluster.py -h
usage: cluster.py [-h] [--debug] {build,start,stop,clean} ...

Create a test MySQL Cluster deployment in docker

positional arguments:
  {build,start,stop,clean}
    build               Build the cluster containers
    start               Start up the cluster containers
    stop                Stop the cluster containers for the specified network
    clean               Stop and remove the cluster containers

optional arguments:
  -h, --help            show this help message and exit
  --debug               Whether to print debug info (default: false)
```

The script takes care of creating the cluster.ini file (using the config.ini.in file as a base template) in the build stage, and then starts up the cluster using the same configuration in the start stage. You must therefore invoke cluster.py with both the build and start corresponding arguments being the same, as the initial number of ndb nodes must be as configured  , before the cluster will complete initialization.

For a simple installation test environment this is as simple as:

```
$ cluster.py build
2016-10-28T09:05:57.051000: Running: docker build -t markleith/mysql-cluster-mgmd:7.5 -f management-node/Dockerfile management-node
2016-10-28T09:06:06.495000: Running: docker build -t markleith/mysql-cluster-ndbmtd:7.5 -f data-node/Dockerfile data-node
2016-10-28T09:06:06.751000: Running: docker build -t markleith/mysql-cluster-sql:7.5 -f sql-node/Dockerfile sql-node

$ cluster.py start
2016-10-28T09:06:25.565000: Running: docker network ls
2016-10-28T09:06:25.622000: Info: mycluster network not found, creating
2016-10-28T09:06:25.624000: Running: docker network create --subnet=172.18.0.0/16 mycluster
2016-10-28T09:06:26.031000: Running: docker ps -q -a --filter "name=mycluster-mgmd49"
2016-10-28T09:06:26.087000: Running: docker run -d -P --net mycluster --name mycluster-mgmd49 --ip 172.18.0.149 -e NODE_ID=49 -e NOWAIT=50 -e CONNECTSTRING= markleith/mysql-cluster-mgmd:7.5
2016-10-28T09:06:27.585000: Running: docker port mycluster-mgmd49 1186/tcp
2016-10-28T09:06:27.653000: Running: docker ps -q -a --filter "name=mycluster-mgmd50"
2016-10-28T09:06:27.706000: Running: docker run -d -P --net mycluster --name mycluster-mgmd50 --ip 172.18.0.150 -e NODE_ID=50 -e NOWAIT=49 -e CONNECTSTRING=mycluster-mgmd49:1186 markleith/mysql-cluster-mgmd:7.5
2016-10-28T09:06:29.083000: Running: docker port mycluster-mgmd50 1186/tcp
2016-10-28T09:06:29.146000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd1"
2016-10-28T09:06:29.203000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd1 --ip 172.18.0.11 -e NODE_ID=1 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:30.657000: Running: docker port mycluster-ndbmtd1 11860/tcp
2016-10-28T09:06:30.719000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd2"
2016-10-28T09:06:30.773000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd2 --ip 172.18.0.12 -e NODE_ID=2 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:32.729000: Running: docker port mycluster-ndbmtd2 11860/tcp
2016-10-28T09:06:32.796000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd3"
2016-10-28T09:06:33.064000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd3 --ip 172.18.0.13 -e NODE_ID=3 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:34.660000: Running: docker port mycluster-ndbmtd3 11860/tcp
2016-10-28T09:06:34.723000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd4"
2016-10-28T09:06:34.790000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd4 --ip 172.18.0.14 -e NODE_ID=4 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:36.343000: Running: docker port mycluster-ndbmtd4 11860/tcp
2016-10-28T09:06:36.403000: Running: docker ps -q -a --filter "name=mycluster-sql51"
2016-10-28T09:06:36.473000: Running: docker run -d -P --net mycluster --name mycluster-sql51 --ip 172.18.0.151 -e NODE_ID=51 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T09:06:45.207000: Running: docker port mycluster-sql51 3306/tcp
2016-10-28T09:06:45.270000: Running: docker ps -q -a --filter "name=mycluster-sql52"
2016-10-28T09:06:45.419000: Running: docker run -d -P --net mycluster --name mycluster-sql52 --ip 172.18.0.152 -e NODE_ID=52 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T09:06:47.762000: Running: docker port mycluster-sql52 3306/tcp
2016-10-28T09:06:47.983000: Info: Started: [ "node" : { "name" : "mycluster-mgmd49", "bound_port" : 33036, "node_type" : "mgmd" } ,  "node" : { "name" : "mycluster-mgmd50", "bound_port" : 33037, "node_type" : "mgmd" } ,  "node" : { "name" : "mycluster-ndbmtd1", "bound_port" : 33038, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd2", "bound_port" : 33039, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd3", "bound_port" : 33040, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd4", "bound_port" : 33041, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-sql51", "bound_port" : 33042, "node_type" : "sql" } ,  "node" : { "name" : "mycluster-sql52", "bound_port" : 33043, "node_type" : "sql" } ]
```

By default cluster.py builds and starts a docker network called `mycluster`, and within it a cluster containing 2 management nodes, 4 data nodes and 2 SQL nodes.

#### Starting multiple clusters

To start multiple clusters on the same host, we need to have a unique naming scheme for the container names, and a unique network IP range to run each cluster network over. These are provided by the `--name` and `--base-network` parameters (or `-n` and `-b`).

As long as you provide unique values for the `--base-network` parameter when running both the `build` and `start` commands, and a unique `--name` whilst using `start`, then you can run two clusters of any shape relatively easily:

```
$ cluster.py build --base-network 172.18 --management-nodes 1 --data-nodes 2 --sql-nodes 1
2016-10-28T10:06:23.308000: Running: docker build -t markleith/mysql-cluster-mgmd:7.5 -f management-node/Dockerfile management-node
2016-10-28T10:06:32.208000: Running: docker build -t markleith/mysql-cluster-ndbmtd:7.5 -f data-node/Dockerfile data-node
2016-10-28T10:06:32.539000: Running: docker build -t markleith/mysql-cluster-sql:7.5 -f sql-node/Dockerfile sql-node

$ cluster.py start --name myc1 --base-network 172.18 --management-nodes 1 --data-nodes 2 --sql-nodes 1
2016-10-28T10:06:46.656000: Running: docker network ls
2016-10-28T10:06:46.712000: Info: myc1 network not found, creating
2016-10-28T10:06:46.714000: Running: docker network create --subnet=172.18.0.0/16 myc1
2016-10-28T10:06:47.132000: Running: docker ps -q -a --filter "name=myc1-mgmd49"
2016-10-28T10:06:47.202000: Running: docker run -d -P --net myc1 --name myc1-mgmd49 --ip 172.18.0.149 -e NODE_ID=49 -e NOWAIT=50 -e CONNECTSTRING= markleith/mysql-cluster-mgmd:7.5
2016-10-28T10:06:48.550000: Running: docker port myc1-mgmd49 1186/tcp
2016-10-28T10:06:48.619000: Running: docker ps -q -a --filter "name=myc1-ndbmtd1"
2016-10-28T10:06:48.670000: Running: docker run -d -P --net myc1 --name myc1-ndbmtd1 --ip 172.18.0.11 -e NODE_ID=1 -e CONNECTSTRING=myc1-mgmd49:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T10:06:50.211000: Running: docker port myc1-ndbmtd1 11860/tcp
2016-10-28T10:06:50.298000: Running: docker ps -q -a --filter "name=myc1-ndbmtd2"
2016-10-28T10:06:50.359000: Running: docker run -d -P --net myc1 --name myc1-ndbmtd2 --ip 172.18.0.12 -e NODE_ID=2 -e CONNECTSTRING=myc1-mgmd49:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T10:06:51.838000: Running: docker port myc1-ndbmtd2 11860/tcp
2016-10-28T10:06:51.889000: Running: docker ps -q -a --filter "name=myc1-sql51"
2016-10-28T10:06:51.945000: Running: docker run -d -P --net myc1 --name myc1-sql51 --ip 172.18.0.151 -e NODE_ID=51 -e CONNECTSTRING=myc1-mgmd49:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T10:06:53.389000: Running: docker port myc1-sql51 3306/tcp
2016-10-28T10:06:53.448000: Info: Started: [ "node" : { "name" : "myc1-mgmd49", "bound_port" : 33052, "node_type" : "mgmd" } ,  "node" : { "name" : "myc1-ndbmtd1", "bound_port" : 33053, "node_type" : "ndbmtd" } ,  "node" : { "name" : "myc1-ndbmtd2", "bound_port" : 33054, "node_type" : "ndbmtd" } ,  "node" : { "name" : "myc1-sql51", "bound_port" : 33055, "node_type" : "sql" } ]

$ cluster.py build --base-network 172.19 --management-nodes 2 --data-nodes 2 --sql-nodes 2
2016-10-28T10:07:23.486000: Running: docker build -t markleith/mysql-cluster-mgmd:7.5 -f management-node/Dockerfile management-node
2016-10-28T10:07:42.201000: Running: docker build -t markleith/mysql-cluster-ndbmtd:7.5 -f data-node/Dockerfile data-node
2016-10-28T10:07:42.482000: Running: docker build -t markleith/mysql-cluster-sql:7.5 -f sql-node/Dockerfile sql-node

$ cluster.py start --name myc2 --base-network 172.19 --management-nodes 2 --data-nodes 2 --sql-nodes 2
2016-10-28T10:07:56.739000: Running: docker network ls
2016-10-28T10:07:56.798000: Info: myc2 network not found, creating
2016-10-28T10:07:56.800000: Running: docker network create --subnet=172.19.0.0/16 myc2
2016-10-28T10:07:57.432000: Running: docker ps -q -a --filter "name=myc2-mgmd49"
2016-10-28T10:07:57.592000: Running: docker run -d -P --net myc2 --name myc2-mgmd49 --ip 172.19.0.149 -e NODE_ID=49 -e NOWAIT=50 -e CONNECTSTRING= markleith/mysql-cluster-mgmd:7.5
2016-10-28T10:07:59.850000: Running: docker port myc2-mgmd49 1186/tcp
2016-10-28T10:07:59.903000: Running: docker ps -q -a --filter "name=myc2-mgmd50"
2016-10-28T10:07:59.954000: Running: docker run -d -P --net myc2 --name myc2-mgmd50 --ip 172.19.0.150 -e NODE_ID=50 -e NOWAIT=49 -e CONNECTSTRING=myc2-mgmd49:1186 markleith/mysql-cluster-mgmd:7.5
2016-10-28T10:08:02.066000: Running: docker port myc2-mgmd50 1186/tcp
2016-10-28T10:08:02.120000: Running: docker ps -q -a --filter "name=myc2-ndbmtd1"
2016-10-28T10:08:02.187000: Running: docker run -d -P --net myc2 --name myc2-ndbmtd1 --ip 172.19.0.11 -e NODE_ID=1 -e CONNECTSTRING=myc2-mgmd49:1186,myc2-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T10:08:04.644000: Running: docker port myc2-ndbmtd1 11860/tcp
2016-10-28T10:08:04.700000: Running: docker ps -q -a --filter "name=myc2-ndbmtd2"
2016-10-28T10:08:04.758000: Running: docker run -d -P --net myc2 --name myc2-ndbmtd2 --ip 172.19.0.12 -e NODE_ID=2 -e CONNECTSTRING=myc2-mgmd49:1186,myc2-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T10:08:08.152000: Running: docker port myc2-ndbmtd2 11860/tcp
2016-10-28T10:08:08.232000: Running: docker ps -q -a --filter "name=myc2-sql51"
2016-10-28T10:08:08.281000: Running: docker run -d -P --net myc2 --name myc2-sql51 --ip 172.19.0.151 -e NODE_ID=51 -e CONNECTSTRING=myc2-mgmd49:1186,myc2-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T10:08:17.201000: Running: docker port myc2-sql51 3306/tcp
2016-10-28T10:08:17.283000: Running: docker ps -q -a --filter "name=myc2-sql52"
2016-10-28T10:08:17.348000: Running: docker run -d -P --net myc2 --name myc2-sql52 --ip 172.19.0.152 -e NODE_ID=52 -e CONNECTSTRING=myc2-mgmd49:1186,myc2-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T10:08:29.808000: Running: docker port myc2-sql52 3306/tcp
2016-10-28T10:08:30.127000: Info: Started: [ "node" : { "name" : "myc2-mgmd49", "bound_port" : 33056, "node_type" : "mgmd" } ,  "node" : { "name" : "myc2-mgmd50", "bound_port" : 33057, "node_type" : "mgmd" } ,  "node" : { "name" : "myc2-ndbmtd1", "bound_port" : 33058, "node_type" : "ndbmtd" } ,  "node" : { "name" : "myc2-ndbmtd2", "bound_port" : 33059, "node_type" : "ndbmtd" } ,  "node" : { "name" : "myc2-sql51", "bound_port" : 33060, "node_type" : "sql" } ,  "node" : { "name" : "myc2-sql52", "bound_port" : 33061, "node_type" : "sql" } ]

$ docker ps
CONTAINER ID        IMAGE                                COMMAND                  CREATED              STATUS              PORTS                      NAMES
e32d4ae024fc        markleith/mysql-cluster-sql:7.5      "/home/mysql/run-mysq"   21 seconds ago       Up 9 seconds        0.0.0.0:33061->3306/tcp    myc2-sql52
038ce476e860        markleith/mysql-cluster-sql:7.5      "/home/mysql/run-mysq"   30 seconds ago       Up 20 seconds       0.0.0.0:33060->3306/tcp    myc2-sql51
32d202bd5d2d        markleith/mysql-cluster-ndbmtd:7.5   "/home/mysql/run-data"   34 seconds ago       Up 29 seconds       0.0.0.0:33059->11860/tcp   myc2-ndbmtd2
0b8f06de740a        markleith/mysql-cluster-ndbmtd:7.5   "/home/mysql/run-data"   36 seconds ago       Up 32 seconds       0.0.0.0:33058->11860/tcp   myc2-ndbmtd1
83bd9674e339        markleith/mysql-cluster-mgmd:7.5     "/home/mysql/run-mgmd"   39 seconds ago       Up 35 seconds       0.0.0.0:33057->1186/tcp    myc2-mgmd50
36cea82543f0        markleith/mysql-cluster-mgmd:7.5     "/home/mysql/run-mgmd"   41 seconds ago       Up 37 seconds       0.0.0.0:33056->1186/tcp    myc2-mgmd49
613b6c18ebd6        markleith/mysql-cluster-sql:7.5      "/home/mysql/run-mysq"   About a minute ago   Up About a minute   0.0.0.0:33055->3306/tcp    myc1-sql51
31b739edcdb4        markleith/mysql-cluster-ndbmtd:7.5   "/home/mysql/run-data"   About a minute ago   Up About a minute   0.0.0.0:33054->11860/tcp   myc1-ndbmtd2
18e19136accb        markleith/mysql-cluster-ndbmtd:7.5   "/home/mysql/run-data"   About a minute ago   Up About a minute   0.0.0.0:33053->11860/tcp   myc1-ndbmtd1
721b3abb7140        a62fba3c15f2                         "/home/mysql/run-mgmd"   About a minute ago   Up About a minute   0.0.0.0:33052->1186/tcp    myc1-mgmd49

```

#### `build` command:

##### Options

```
usage: cluster.py build [-h] [-b BASE_NETWORK] [-m MANAGEMENT_NODES]
                        [-d DATA_NODES] [-s SQL_NODES]

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_NETWORK, --base-network BASE_NETWORK
                        The base IP network range (default: 172.18)
  -m MANAGEMENT_NODES, --management-nodes MANAGEMENT_NODES
                        Number of Management nodes to run (default: 2; max: 2)
  -d DATA_NODES, --data-nodes DATA_NODES
                        Number of NDB nodes to run (default: 4; max: 48)
  -s SQL_NODES, --sql-nodes SQL_NODES
                        Number of SQL nodes to run (default: 2)
```

##### Example

```
$ cluster.py build
2016-10-28T09:05:57.051000: Running: docker build -t markleith/mysql-cluster-mgmd:7.5 -f management-node/Dockerfile management-node
2016-10-28T09:06:06.495000: Running: docker build -t markleith/mysql-cluster-ndbmtd:7.5 -f data-node/Dockerfile data-node
2016-10-28T09:06:06.751000: Running: docker build -t markleith/mysql-cluster-sql:7.5 -f sql-node/Dockerfile sql-node
```

#### `start` command:

##### Options

```
usage: cluster.py start [-h] [-n NAME] [-b BASE_NETWORK] [-m MANAGEMENT_NODES]
                        [-d DATA_NODES] [-s SQL_NODES]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  The prefix to use for managing the network and
                        containers (default: mycluster)
  -b BASE_NETWORK, --base-network BASE_NETWORK
                        The base IP network range (default: 172.18)
  -m MANAGEMENT_NODES, --management-nodes MANAGEMENT_NODES
                        Number of Management nodes to run (default: 2; max: 2)
  -d DATA_NODES, --data-nodes DATA_NODES
                        Number of NDB nodes to run (default: 4; max: 48)
  -s SQL_NODES, --sql-nodes SQL_NODES
                        Number of SQL nodes to run (default: 2)
```

```
$ cluster.py start
2016-10-28T09:06:25.565000: Running: docker network ls
2016-10-28T09:06:25.622000: Info: mycluster network not found, creating
2016-10-28T09:06:25.624000: Running: docker network create --subnet=172.18.0.0/16 mycluster
2016-10-28T09:06:26.031000: Running: docker ps -q -a --filter "name=mycluster-mgmd49"
2016-10-28T09:06:26.087000: Running: docker run -d -P --net mycluster --name mycluster-mgmd49 --ip 172.18.0.149 -e NODE_ID=49 -e NOWAIT=50 -e CONNECTSTRING= markleith/mysql-cluster-mgmd:7.5
2016-10-28T09:06:27.585000: Running: docker port mycluster-mgmd49 1186/tcp
2016-10-28T09:06:27.653000: Running: docker ps -q -a --filter "name=mycluster-mgmd50"
2016-10-28T09:06:27.706000: Running: docker run -d -P --net mycluster --name mycluster-mgmd50 --ip 172.18.0.150 -e NODE_ID=50 -e NOWAIT=49 -e CONNECTSTRING=mycluster-mgmd49:1186 markleith/mysql-cluster-mgmd:7.5
2016-10-28T09:06:29.083000: Running: docker port mycluster-mgmd50 1186/tcp
2016-10-28T09:06:29.146000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd1"
2016-10-28T09:06:29.203000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd1 --ip 172.18.0.11 -e NODE_ID=1 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:30.657000: Running: docker port mycluster-ndbmtd1 11860/tcp
2016-10-28T09:06:30.719000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd2"
2016-10-28T09:06:30.773000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd2 --ip 172.18.0.12 -e NODE_ID=2 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:32.729000: Running: docker port mycluster-ndbmtd2 11860/tcp
2016-10-28T09:06:32.796000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd3"
2016-10-28T09:06:33.064000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd3 --ip 172.18.0.13 -e NODE_ID=3 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:34.660000: Running: docker port mycluster-ndbmtd3 11860/tcp
2016-10-28T09:06:34.723000: Running: docker ps -q -a --filter "name=mycluster-ndbmtd4"
2016-10-28T09:06:34.790000: Running: docker run -d -P --net mycluster --name mycluster-ndbmtd4 --ip 172.18.0.14 -e NODE_ID=4 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-ndbmtd:7.5
2016-10-28T09:06:36.343000: Running: docker port mycluster-ndbmtd4 11860/tcp
2016-10-28T09:06:36.403000: Running: docker ps -q -a --filter "name=mycluster-sql51"
2016-10-28T09:06:36.473000: Running: docker run -d -P --net mycluster --name mycluster-sql51 --ip 172.18.0.151 -e NODE_ID=51 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T09:06:45.207000: Running: docker port mycluster-sql51 3306/tcp
2016-10-28T09:06:45.270000: Running: docker ps -q -a --filter "name=mycluster-sql52"
2016-10-28T09:06:45.419000: Running: docker run -d -P --net mycluster --name mycluster-sql52 --ip 172.18.0.152 -e NODE_ID=52 -e CONNECTSTRING=mycluster-mgmd49:1186,mycluster-mgmd50:1186 markleith/mysql-cluster-sql:7.5
2016-10-28T09:06:47.762000: Running: docker port mycluster-sql52 3306/tcp
2016-10-28T09:06:47.983000: Info: Started: [ "node" : { "name" : "mycluster-mgmd49", "bound_port" : 33036, "node_type" : "mgmd" } ,  "node" : { "name" : "mycluster-mgmd50", "bound_port" : 33037, "node_type" : "mgmd" } ,  "node" : { "name" : "mycluster-ndbmtd1", "bound_port" : 33038, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd2", "bound_port" : 33039, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd3", "bound_port" : 33040, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-ndbmtd4", "bound_port" : 33041, "node_type" : "ndbmtd" } ,  "node" : { "name" : "mycluster-sql51", "bound_port" : 33042, "node_type" : "sql" } ,  "node" : { "name" : "mycluster-sql52", "bound_port" : 33043, "node_type" : "sql" } ]
```

#### `stop` command:

##### Options

```
usage: cluster.py stop [-h] [-n NAME]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  The prefix to use for managing the network and
                        containers (default: mycluster)
```

##### Example

```
$ cluster.py stop
2016-10-28T09:29:38.076000: Running: docker network ls
2016-10-28T09:29:38.391000: Running: docker network inspect --format="{{range $i, $c := .Containers}}{{$i}},{{end}}" mycluster
2016-10-28T09:29:38.456000: Running: docker stop 3c781c3517a2 41c3bfcba7d1 4210e83036a3 66289dc0b529 7bb378282d22 afd8d427c751 f021167e7be7 fc0de2b342ff
2016-10-28T09:31:03.673000: Info: Stopping containers done
```

#### `clean` command:

##### Options

```
usage: cluster.py clean [-h] [-n NAME] [-i] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  The prefix to use for managing the network and
                        containers (default: mycluster)
  -i, --images          Delete markleith/mysql-cluster docker images (default:
                        false)
  -d, --dangling        Delete dangling docker images (default: false)
```

##### Example

```
$ cluster.py clean
2016-10-28T09:54:31.418000: Running: docker ps -a --filter "ancestor=markleith/mysql-cluster-mgmd:7.5" --format "{{.ID}}"
2016-10-28T09:54:31.499000: Running: docker ps -a --filter "ancestor=markleith/mysql-cluster-ndbmtd:7.5" --format "{{.ID}}"
2016-10-28T09:54:31.565000: Running: docker ps -a --filter "ancestor=markleith/mysql-cluster-sql:7.5" --format "{{.ID}}"
2016-10-28T09:54:31.626000: Running: docker stop 66289dc0b529 3c781c3517a2 afd8d427c751 7bb378282d22 f021167e7be7 41c3bfcba7d1 fc0de2b342ff 4210e83036a3
2016-10-28T09:55:53.496000: Running: docker rm 66289dc0b529 3c781c3517a2 afd8d427c751 7bb378282d22 f021167e7be7 41c3bfcba7d1 fc0de2b342ff 4210e83036a3
2016-10-28T09:55:55.302000: Running: docker network ls
2016-10-28T09:55:55.404000: Running: docker network rm mycluster
2016-10-28T09:55:56.036000: Running: docker network ls
```

#### Connecting

You can use the exposed ports to connect directly to a SQL node from the docker host OS, such as taking the exposed port for mysqlndb52 above (33043):

```
$ mysql -u root -pmysql -h 127.0.0.1 -P 33043
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 4
Server version: 5.7.16-ndb-7.5.4-cluster-gpl MySQL Cluster Community Server (GPL)

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show tables from ndbinfo;
+---------------------------------+
| Tables_in_ndbinfo               |
+---------------------------------+
| arbitrator_validity_detail      |
| arbitrator_validity_summary     |
| blocks                          |
| cluster_locks                   |
| cluster_operations              |
| cluster_transactions            |
| config_params                   |
| config_values                   |
| counters                        |
| cpustat                         |
| cpustat_1sec                    |
| cpustat_20sec                   |
| cpustat_50ms                    |
| dict_obj_info                   |
| dict_obj_types                  |
| disk_write_speed_aggregate      |
| disk_write_speed_aggregate_node |
| disk_write_speed_base           |
| diskpagebuffer                  |
| locks_per_fragment              |
| logbuffers                      |
| logspaces                       |
| membership                      |
| memory_per_fragment             |
| memoryusage                     |
| nodes                           |
| operations_per_fragment         |
| resources                       |
| restart_info                    |
| server_locks                    |
| server_operations               |
| server_transactions             |
| table_distribution_status       |
| table_fragments                 |
| table_info                      |
| table_replicas                  |
| tc_time_track_stats             |
| threadblocks                    |
| threads                         |
| threadstat                      |
| transporters                    |
+---------------------------------+
41 rows in set (0.00 sec)

mysql> desc ndbinfo.memoryusage;
+-------------+------------------+------+-----+---------+-------+
| Field       | Type             | Null | Key | Default | Extra |
+-------------+------------------+------+-----+---------+-------+
| node_id     | int(10) unsigned | YES  |     | NULL    |       |
| memory_type | varchar(512)     | YES  |     | NULL    |       |
| used        | decimal(62,0)    | YES  |     | NULL    |       |
| used_pages  | decimal(42,0)    | YES  |     | NULL    |       |
| total       | decimal(62,0)    | YES  |     | NULL    |       |
| total_pages | decimal(42,0)    | YES  |     | NULL    |       |
+-------------+------------------+------+-----+---------+-------+
6 rows in set (0.10 sec)

mysql> select node_id, memory_type, sys.format_bytes(used) used, sys.format_bytes(total) total from ndbinfo.memoryusage;
+---------+---------------------+------------+-----------+
| node_id | memory_type         | used       | total     |
+---------+---------------------+------------+-----------+
|       1 | Data memory         | 704.00 KiB | 80.00 MiB |
|       1 | Index memory        | 104.00 KiB | 18.25 MiB |
|       1 | Long message buffer | 384.00 KiB | 32.00 MiB |
|       2 | Data memory         | 704.00 KiB | 80.00 MiB |
|       2 | Index memory        | 104.00 KiB | 18.25 MiB |
|       2 | Long message buffer | 256.00 KiB | 32.00 MiB |
|       3 | Data memory         | 704.00 KiB | 80.00 MiB |
|       3 | Index memory        | 104.00 KiB | 18.25 MiB |
|       3 | Long message buffer | 256.00 KiB | 32.00 MiB |
|       4 | Data memory         | 704.00 KiB | 80.00 MiB |
|       4 | Index memory        | 104.00 KiB | 18.25 MiB |
|       4 | Long message buffer | 256.00 KiB | 32.00 MiB |
+---------+---------------------+------------+-----------+
12 rows in set (0.42 sec)
```

### mysql-repo-server-5.6-centos-6.8

Sets up CentOS 6.8 with SSH and MySQL started.

MySQL is installed from the [MySQL Yum repository](http://dev.mysql.com/downloads/repo/yum/).

#### Build:

```
cd ./hosts/centos-6.8
docker build -t markleith/centos-6.8 .
cd ../../mysql-repo-server-5.6-centos-6.8
docker build -t markleith/mysql-repo-server-5.6-centos-6.8 .
```

#### Run:
```
docker run -d -P --name my56centos68 markleith/mysql-repo-server-5.6-centos-6.8
```

### mysql-repo-server-5.6-ubuntu-14.04

Sets up Ubuntu 14.04 with SSH and MySQL started.

MySQL is installed from the [MySQL Apt Repository](http://dev.mysql.com/downloads/repo/apt/).

#### Build:

```
cd ./hosts/ubuntu-14.04
docker build -t markleith/ubuntu-14.04 .
cd ../mysql-repo-server-5.6-ubuntu-14.04
docker build -t markleith/mysql-repo-server-5.6-ubuntu-14.04 .
```

#### Run:
```
docker run -d -P --name my56ubuntu1404 markleith/mysql-repo-server-5.6-ubuntu-14.04
```

## Sysbench 0.5

There is a generic container available to run sysbench benchmarks from. This builds sysbench directly from the Launchpad bzr tree.

It can be used to run any sysbench and allows spinning up multiple docker containers to drive benchmark load.

To point to another container on the same host, use the "Network Gateway" address from `docker inspect`, as well as the port that is exposed for 3306.

Linking, or running against non-docker MySQL hosts is also of course feasible. The containers will shut down as soon as their benchmarks are complete.

#### Run:

```
$ docker run -i -t --name=sysb01 markleith/sysbench-0.5 /usr/local/bin/sysbench \
> --test=/sysbench/sysbench/tests/db/oltp_simple.lua --mysql-table-engine=InnoDB \
> --mysql-user=root --mysql-password=mysql --mysql-host=172.17.42.1 --mysql-port=49189 \
> --num-threads=8 --max-requests=20000 --report-interval=1 run
sysbench 0.5:  multi-threaded system evaluation benchmark

Running the test with following options:
Number of threads: 8
Report intermediate results every 1 second(s)
Random number generator seed is 0 and will be ignored


Threads started!

[   1s] threads: 8, tps: 0.00, reads/s: 2799.35, writes/s: 0.00, response time: 5.99ms (95%)
[   2s] threads: 8, tps: 0.00, reads/s: 2808.92, writes/s: 0.00, response time: 5.66ms (95%)
[   3s] threads: 8, tps: 0.00, reads/s: 2437.41, writes/s: 0.00, response time: 8.89ms (95%)
[   4s] threads: 8, tps: 0.00, reads/s: 2824.45, writes/s: 0.00, response time: 7.14ms (95%)
[   5s] threads: 8, tps: 0.00, reads/s: 2907.49, writes/s: 0.00, response time: 6.58ms (95%)
[   6s] threads: 8, tps: 0.00, reads/s: 2924.48, writes/s: 0.00, response time: 5.54ms (95%)
[   7s] threads: 8, tps: 0.00, reads/s: 2396.74, writes/s: 0.00, response time: 11.32ms (95%)
OLTP test statistics:
    queries performed:
        read:                            20000
        write:                           0
        other:                           0
        total:                           20000
    transactions:                        0      (0.00 per sec.)
    deadlocks:                           0      (0.00 per sec.)
    read/write requests:                 20000  (2727.52 per sec.)
    other operations:                    0      (0.00 per sec.)

General statistics:
    total time:                          7.3327s
    total number of events:              20000
    total time taken by event execution: 57.9213s
    response time:
         min:                                  0.00ms
         avg:                                  2.90ms
         max:                                 69.77ms
         approx.  95 percentile:               7.02ms

Threads fairness:
    events (avg/stddev):           2500.0000/179.43
    execution time (avg/stddev):   7.2402/0.02
```


## Base Hosts

Each of the base hosts install a certain set of base packages (vim, git, gdb, open-ssh). 

SSH is configured so that you can log in to each container, and debug MySQL issues locally (such as being able to also run in gdb).

Supported hosts are:

* CentOS 6.8
* Ubuntu 14.04

All host root passwords are set to root.
