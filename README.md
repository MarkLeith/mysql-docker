mysql-docker
============

Docker configurations for running MySQL deployments.

## MySQL Flavors

### mysql-repo-server-centos-6.4

Sets up CentOS 6.4 with SSH and MySQL started.

Build:

```
docker build -t markleith/mysql-repo-server-centos-6.4
```

Run:
```
docker run -d -P -name markleith/mysql-repo-server-centos-6.4
```

## Base Hosts

### centos-6.4

Sets up base image of CentOS 6.4 with SSH.

Build:

```
docker build -t markleith/centos-6.4
```

Run:

```
docker run -i -t markleith/centos-6.4
```

