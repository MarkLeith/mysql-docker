#!/bin/bash
set -e

CMD="/usr/sbin/ndb_mgmd -f /etc/mysql/cluster/config.ini --initial --nodaemon --ndb-nodeid=$NODE_ID --nowait-nodes=$NOWAIT"

if [ "$CONNECTSTRING" != '' ]; then
	CMD="$CMD --ndb-connectstring=$CONNECTSTRING"
fi

echo ""
echo "Running $CMD"
echo ""

exec $CMD
