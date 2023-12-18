#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
if [ ! -e "$SCRIPT_DIR/../.env" ] ; then
    cp "$SCRIPT_DIR/../.env.dist" "$SCRIPT_DIR/../.env"
fi
exec "$SCRIPT_DIR/../../kit/kit" "$SCRIPT_DIR/nova.opc_usd.kit" "$@"
