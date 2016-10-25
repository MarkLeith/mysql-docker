mysql-docker
============

Docker configurations for running MySQL deployments.

## MySQL Flavors

All MySQL instances are configured to listen on port 3306 (the default), with the following users able to connect from all hosts:

* root / mysql (the default SUPER user)
* repl / repl (a replication user)
* fabric / fabric (a MySQL Fabric user)
* mem / mem (a MySQL Enterprise Monitor user)

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
