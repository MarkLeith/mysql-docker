FROM markleith/centos-6.8

MAINTAINER Mark Leith (mark@markleith.co.uk)

RUN rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm
RUN yum -y install mysql-community-devel mysql-community-client

RUN yum -y install automake libtool gcc

RUN bzr branch lp:sysbench
RUN cd sysbench && ./autogen.sh && ./configure --without-drizzle --with-mysql --with-mysql-includes=/usr/include/mysql --with-mysql-libs=/usr/lib64/mysql && make && make install

