FROM oraclelinux:latest

MAINTAINER Mark Leith (mark@markleith.co.uk)

RUN yum install -y https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.5/mysql-cluster-community-management-server-7.5.4-1.el7.x86_64.rpm

RUN mkdir -p /var/lib/ndb/management
RUN mkdir -p /etc/mysql/cluster
ADD config.ini /etc/mysql/cluster/config.ini
RUN chmod 644 /etc/mysql/cluster/config.ini

EXPOSE 1186

ADD run.sh /home/mysql/run-mgmd.sh
RUN chmod +x /home/mysql/run-mgmd.sh
ENTRYPOINT ["/home/mysql/run-mgmd.sh"]
