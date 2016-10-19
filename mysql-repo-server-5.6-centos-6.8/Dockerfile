FROM markleith/centos-6.8

MAINTAINER Mark Leith (mark@markleith.co.uk)

RUN rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm
RUN yum -y install mysql-community-server

RUN git clone https://github.com/MarkLeith/mysql-sys.git /tmp/mysql-sys

ADD mysql-init /usr/bin/mysql-init
RUN chmod +x /usr/bin/mysql-init
RUN /usr/bin/mysql-init

ADD mysql-start /usr/bin/mysql-start
RUN chmod +x /usr/bin/mysql-start

ADD my.cnf /etc/my.cnf

EXPOSE 22 3306

ENTRYPOINT ["/usr/bin/mysql-start"]

