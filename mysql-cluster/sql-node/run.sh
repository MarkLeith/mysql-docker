#!/bin/bash

DATADIR="$(/usr/sbin/mysqld --verbose --help --log-bin-index=/tmp/tmp.index 2>/dev/null | awk '$1 == "datadir" { print $2; exit }')"

wait_for_mysql() {
	for i in {1..30}; do
		mysql -u root -S /tmp/mysql.sock -e "SELECT 1" &> /dev/null
		if [[ "$?" == "0" ]] ; then
			break
		fi
		sleep 1
	done
	if [ "$i" = 0 ]; then
		echo "MySQL init process failed!"
		exit 1
	fi
}

if [ ! -d "$DATADIR/mysql" ]; then
	echo "No database found, initializing..."
	/usr/sbin/mysqld --user=mysql --initialize-insecure=on

	echo "Setting credentials..."
	/usr/sbin/mysqld --no-defaults --user=mysql --console --skip-networking --socket=/tmp/mysql.sock &
	pid="$!"

	wait_for_mysql

	mysql -e " \
		SET @@SESSION.SQL_LOG_BIN=0; \
		DELETE FROM mysql.user WHERE user NOT IN ('mysql.sys', 'mysqlxsys'); \
		CREATE USER 'root'@'%' IDENTIFIED BY 'mysql'; \
		GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION; \
		CREATE USER 'repl'@'%' IDENTIFIED BY 'repl'; \
		GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%'; \
		CREATE USER 'mem'@'%' IDENTIFIED BY 'mem'; \
		GRANT SELECT, SHOW DATABASES, SUPER, REPLICATION CLIENT, PROCESS ON *.* TO 'mem'@'%'; \
		FLUSH PRIVILEGES;"

	if ! kill -s TERM "$pid" || ! wait "$pid"; then
		echo "MySQL init process failed!"
		exit 1
	fi
fi

CMD="/usr/sbin/mysqld --user=mysql --ndb-nodeid=$NODE_ID --ndb-connectstring=$CONNECTSTRING --server-id=$NODE_ID"

echo "Running: $CMD"

exec $CMD
