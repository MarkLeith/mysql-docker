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
    stop                Stop the cluster containers
    clean               Stop and remove the cluster containers

optional arguments:
  -h, --help            show this help message and exit
  --debug               Whether to print debug info

$ cluster.py build -h
usage: cluster.py build [-h] [-m MANAGEMENT_NODES] [-d DATA_NODES]
                        [-s SQL_NODES]

optional arguments:
  -h, --help            show this help message and exit
  -m MANAGEMENT_NODES, --management-nodes MANAGEMENT_NODES
                        Number of Management nodes to run (default: 2; max: 2)
  -d DATA_NODES, --data-nodes DATA_NODES
                        Number of NDB nodes to run (default: 4; max: 48)
  -s SQL_NODES, --sql-nodes SQL_NODES
                        Number of SQL nodes to run (default: 2)

$ cluster.py start -h
usage: cluster.py start [-h] [-n NETWORK] [-m MANAGEMENT_NODES]
                        [-d DATA_NODES] [-s SQL_NODES]

optional arguments:
  -h, --help            show this help message and exit
  -n NETWORK, --network NETWORK
                        Name of the docker network to use
  -m MANAGEMENT_NODES, --management-nodes MANAGEMENT_NODES
                        Number of Management nodes to run (default: 2; max: 2)
  -d DATA_NODES, --data-nodes DATA_NODES
                        Number of NDB nodes to run (default: 4; max: 48)
  -s SQL_NODES, --sql-nodes SQL_NODES
                        Number of SQL nodes to run (default: 2)
```

You must invoke this with both the build and start arguments being the same, as the build command builds the initial cluster.ini file, which is then used when started using the start command - the initial number of ndb nodes must be as expected when started.

#### Build:

```
$ cluster.py --debug build
2016-10-25T16:04:33.229000: Arguments: Namespace(data_nodes=4, debug=True, func=<function build at 0x0000000002E63BA8>, management_nodes=2, sql_nodes=2)
2016-10-25T16:04:33.235000: Running: docker build -t markleith/mysqlcluster75:ndb_mgmd -f management-node/Dockerfile management-node
2016-10-25T16:04:33.511000: Running: docker build -t markleith/mysqlcluster75:ndbmtd -f data-node/Dockerfile data-node
2016-10-25T16:04:33.809000: Running: docker build -t markleith/mysqlcluster75:sql -f sql-node/Dockerfile sql-node
```

#### Run:

```
$ cluster.py --debug start
2016-10-25T16:04:37.007000: Arguments: Namespace(data_nodes=4, debug=True, func=<function start at 0x0000000002F73C18>, management_nodes=2, network='myclusternet', sql_nodes=2)
2016-10-25T16:04:37.012000: Running: docker network ls
2016-10-25T16:04:37.076000: myclusternet network found, using existing
2016-10-25T16:04:37.078000: Running: docker run -d -P --net myclusternet --name mymgmd49 --ip 172.18.0.249 -e NODE_ID=49 -e NOWAIT=50 -e CONNECTSTRING= markleith/mysqlcluster75:ndb_mgmd
2016-10-25T16:04:38.799000: Running: docker port mymgmd49 1186/tcp
2016-10-25T16:04:38.885000: Added: Node(mymgmd49 : 32800 : mgmd)
2016-10-25T16:04:38.887000: Running: docker run -d -P --net myclusternet --name mymgmd50 --ip 172.18.0.250 -e NODE_ID=50 -e NOWAIT=49 -e CONNECTSTRING=mymgmd49:1186 markleith/mysqlcluster75:ndb_mgmd
2016-10-25T16:04:40.338000: Running: docker port mymgmd50 1186/tcp
2016-10-25T16:04:40.394000: Added: Node(mymgmd50 : 32801 : mgmd)
2016-10-25T16:04:40.396000: Running: docker run -d -P --net myclusternet --name myndbmtd1 --ip 172.18.0.11 -e NODE_ID=1 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:ndbmtd
2016-10-25T16:04:41.925000: Running: docker port myndbmtd1 11860/tcp
2016-10-25T16:04:41.987000: Added: Node(myndbmtd1 : 32802 : ndbmtd)
2016-10-25T16:04:41.989000: Running: docker run -d -P --net myclusternet --name myndbmtd2 --ip 172.18.0.12 -e NODE_ID=2 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:ndbmtd
2016-10-25T16:04:43.280000: Running: docker port myndbmtd2 11860/tcp
2016-10-25T16:04:43.336000: Added: Node(myndbmtd2 : 32803 : ndbmtd)
2016-10-25T16:04:43.338000: Running: docker run -d -P --net myclusternet --name myndbmtd3 --ip 172.18.0.13 -e NODE_ID=3 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:ndbmtd
2016-10-25T16:04:44.855000: Running: docker port myndbmtd3 11860/tcp
2016-10-25T16:04:44.936000: Added: Node(myndbmtd3 : 32804 : ndbmtd)
2016-10-25T16:04:44.937000: Running: docker run -d -P --net myclusternet --name myndbmtd4 --ip 172.18.0.14 -e NODE_ID=4 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:ndbmtd
2016-10-25T16:04:49.039000: Running: docker port myndbmtd4 11860/tcp
2016-10-25T16:04:49.117000: Added: Node(myndbmtd4 : 32805 : ndbmtd)
2016-10-25T16:04:49.119000: Running: docker run -d -P --net myclusternet --name mysqlndb51 --ip 172.18.0.151 -e NODE_ID=51 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:sql
2016-10-25T16:05:06.190000: Running: docker port mysqlndb51 3306/tcp
2016-10-25T16:05:06.264000: Added: Node(mysqlndb51 : 32806 : sql)
2016-10-25T16:05:06.266000: Running: docker run -d -P --net myclusternet --name mysqlndb52 --ip 172.18.0.152 -e NODE_ID=52 -e CONNECTSTRING=mymgmd49:1186,mymgmd50:1186 markleith/mysqlcluster75:sql
2016-10-25T16:05:12.735000: Running: docker port mysqlndb52 3306/tcp
2016-10-25T16:05:13.104000: Added: Node(mysqlndb52 : 32807 : sql)
2016-10-25T16:05:13.105000: Started: [Node(mymgmd49 : 32800 : mgmd), Node(mymgmd50 : 32801 : mgmd), Node(myndbmtd1 : 32802 : ndbmtd), Node(myndbmtd2 : 32803 : ndbmtd), Node(myndbmtd3 : 32804 : ndbmtd), Node(myndbmtd4 : 32805 : ndbmtd), Node(mysqlndb51 : 32806 : sql), Node(mysqlndb52 : 32807 : sql)]
```

#### Connecting

You can use the exposed ports to connect directly to a SQL node from the docker host OS, such as taking the exposed port for mysqlndb52 above (32807):

```
$ mysql -u root -pmysql -h 127.0.0.1 -P 32807
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
