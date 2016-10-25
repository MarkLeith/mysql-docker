#!/bin/bash
set -e

CMD="/usr/sbin/ndbmtd --initial --nodaemon --ndb-nodeid=$NODE_ID --ndb-connectstring=$CONNECTSTRING"

echo ""
echo "Running $CMD"
echo ""

exec $CMD
