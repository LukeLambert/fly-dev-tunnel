#!/usr/bin/env python3

import os

TEMPLATE_HEADER = '''
    map $http_upgrade $proxy_connection {
        default upgrade;
        '' close;
    }
'''

TEMPLATE_SERVER_DEFAULT = '''
    server {
        listen 8080 default_server;
        listen [::]:8080 default_server;
        server_name _;
        location / {
            return 200;
            add_header Content-Type text/plain;
        }
    }
'''

TEMPLATE_SERVER = '''
    server {
        listen 8080;
        listen [::]:8080;
        server_name {{subdomain}}.*;
        location / {
            proxy_pass http://{{upstream}}:{{port}};
            proxy_http_version 1.1;
            proxy_buffering off;
            proxy_set_header Host $http_host;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $proxy_connection;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
            proxy_set_header X-Forwarded-Port $http_x_forwarded_port;
            proxy_set_header Proxy "";
        }
    }
'''

subdomains = dict([s.split(':') for s in os.environ.get('SUBDOMAINS', '').split(',') if s])
upstream = os.environ.get('UPSTREAM', '')
if ':' in upstream:
    upstream = '[' + upstream + ']'
output = TEMPLATE_HEADER
for subdomain, port in subdomains.items():
    template = TEMPLATE_SERVER
    context = {
        'upstream': upstream,
        'subdomain': subdomain,
        'port': port,
    }
    for key, value in context.items():
        template = template.replace('{{' + key + '}}', value)
    output += template
if '_' not in subdomains:
    output += TEMPLATE_SERVER_DEFAULT
with open('/etc/nginx/conf.d/default.conf', 'w') as f:
    f.write(output)
