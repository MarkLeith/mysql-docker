mysql-docker
============

Docker configurations for running MySQL deployments.

## MySQL Flavors

### mysql-repo-server-5.6-centos-6.4

Sets up CentOS 6.4 with SSH and MySQL started.

MySQL is installed from the [MySQL Yum repository](http://dev.mysql.com/downloads/repo/yum/).

#### Build:

```
cd ./servers/centos-6.4
docker build -t markleith/centos-6.4 .
cd ../mysql-repo-server-centos-6.4
docker build -t markleith/mysql-repo-server-5.6-centos-6.4 .
```

#### Run:
```
docker run -d -P --name my56centos64 markleith/mysql-repo-server-5.6-centos-6.4
```

### mysql-repo-server-5.6-ubuntu-14.04

Sets up Ubuntu 14.04 with SSH and MySQL started.

MySQL is installed from the [MySQL Apt Repository](http://dev.mysql.com/downloads/repo/apt/).

#### Build:

```
cd ./servers/ubuntu-14.04
docker build -t markleith/ubuntu-14.04 .
cd ../mysql-repo-server-5.6-ubuntu-14.04
docker build -t markleith/mysql-repo-server-5.6-ubuntu-14.04 .
```

#### Run:
```
docker run -d -P --name my56ubuntu1404 markleith/mysql-repo-server-5.6-ubuntu-14.04
```

## Base Hosts

Each of the base hosts install a certain set of base packages (vim, git, gdb, open-ssh). 

SSH is configured so that you can log in to each container, and debug MySQL issues locally (such as being able to also run in gdb).

Supported hosts are:

* CentOS 6.4
* Ubuntu 14.04

