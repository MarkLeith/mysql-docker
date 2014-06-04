FROM ubuntu:14.04

MAINTAINER Mark Leith (mark@markleith.co.uk)

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q vim bzr git gdb openssh-server

RUN echo 'root:root' | chpasswd
RUN mkdir -p /var/run/sshd

RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/#UsePAM no/UsePAM no/g' /etc/ssh/sshd_config
RUN sed -ri 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config

EXPOSE 22

CMD /usr/sbin/sshd -D
