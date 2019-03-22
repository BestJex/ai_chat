#!/bin/bash

set -e
#cd /opt/ops_platform

#git stash
#git pull origin python3:python3
#
#pip3 install -r requirements.txt


if [ -n "$DB_HOST" ]; then
    sed -i "s@{{\s*DB_HOST\s*}}@$DB_HOST@g" demo/settings.py.template
fi

if [ -n "$DB_NAME" ]; then
    sed -i "s@{{\s*DB_NAME\s*}}@$DB_NAME@g" demo/settings.py.template
fi

if [ -n "$DB_USER" ]; then
    sed -i "s@{{\s*DB_USER\s*}}@$DB_USER@g" demo/settings.py.template
fi

if [ -n "$DB_PASSWORD" ]; then
    sed -i "s@{{\s*DB_PASSWORD\s*}}@$DB_PASSWORD@g" demo/settings.py.template
fi

if [ -n "$DB_PORT" ]; then
    sed -i "s@{{\s*DB_PORT\s*}}@$DB_PORT@g" demo/settings.py.template
fi

if [ -n "$MONGO_HOST" ]; then
    sed -i "s@{{\s*MONGO_HOST\s*}}@$MONGO_HOST@g" demo/settings.py.template
fi

if [ -n "$MONGO_PORT" ]; then
    sed -i "s@{{\s*MONGO_PORT\s*}}@$MONGO_PORT@g" demo/settings.py.template
fi

if [ -n "$ZK_HOST" ]; then
    sed -i "s@{{\s*ZK_HOST\s*}}@$ZK_HOST@g" demo/settings.py.template
fi

if [ -n "$MANAGE_K" ]; then
    sed -i "s@{{\s*MANAGE_K\s*}}@$MANAGE_K@g" demo/settings.py.template
fi

if [ -n "$REDIS_HOST" ]; then
    sed -i "s@{{\s*REDIS_HOST\s*}}@$REDIS_HOST@g" demo/settings.py.template
fi

if [ -n "$REDIS_PSW" ]; then
    sed -i "s@{{\s*REDIS_PSW\s*}}@$REDIS_PSW@g" demo/settings.py.template
fi

mv demo/settings.py.template demo/settings.py

exec "$@"
