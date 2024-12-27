#!/bin/bash

# 启动 nginx
nginx -g 'daemon off;' &

# 启动 django-q
/workdir/salt/bin/python manage.py qcluster &

# 启动 gunicorn
/workdir/salt/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 smartinfra.wsgi:application