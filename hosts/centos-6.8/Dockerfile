FROM centos:6.8

MAINTAINER Mark Leith (mark@markleith.co.uk)

RUN yum -y install vim git bzr gdb openssh-server openssh-clients libaio
RUN yum -y update

RUN echo 'root:root' | chpasswd
RUN mkdir -p /var/run/sshd
RUN ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key && ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN sed -ri 's/#PermitRootLogin yes/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/#UsePAM no/UsePAM no/g' /etc/ssh/sshd_config

EXPOSE 22

CMD /usr/sbin/sshd -D

