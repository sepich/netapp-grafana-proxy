#!/usr/bin/env python
import os
import pwd
import grp
import sys
import signal
import argparse
import threading
import httplib
import urllib2
import json
import ssl
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn


class TServer(ThreadingMixIn, HTTPServer):
    pass


def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        return
    uid = pwd.getpwnam(uid_name).pw_uid
    gid = grp.getgrnam(gid_name).gr_gid
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)


def exit_handler(signal, frame):
    sys.exit(0)


def get_token(config):
    ssl._create_default_https_context = ssl._create_unverified_context
    conn = httplib.HTTPSConnection(config['endpoint'].split('//')[-1])
    conn.request('POST', '/api/v2/authorize', json.dumps(config))
    response = conn.getresponse()
    if response.status == 200:
        return json.load(response)['data']
    sys.exit("{} {}\n{}".format(response.status, response.reason, response.read()))


class HTTPHandler(BaseHTTPRequestHandler):
    api = {'label': 'metric-labels', 'query_range': 'metric-query-range'}

    def do_GET(self):
        global token, config
        try:
            if self.path.startswith('/api/v1/'):
                word = self.path.split('?')[0].split('/')[3]
                if word in self.api:
                    to = config['endpoint'] + self.path.replace('/api/v1/' + word, '/api/v2/grid/' + self.api[word])
                else:
                    to = config['endpoint'] + self.path.replace('/api/v1/', '/api/v2/grid/metric-')

                # retry query if token expired
                for i in range(2):
                    if not token:
                        token = get_token(config)
                    req = urllib2.Request(url=to, headers={"Authorization": "Bearer " + token})
                    try:
                        resp = urllib2.urlopen(req)
                        code = resp.getcode()
                        break
                    except urllib2.HTTPError as e:
                        if e.code in [401, 403]:
                            token = ''
                        else:
                            raise e

                self.send_response(code)
                for header in resp.info().headers:
                    h = [x.strip() for x in header.split(':', 1)]
                    if len(h) == 2:
                        self.send_header(*h)
                self.end_headers()
                self.wfile.write(resp.read())
        except:
            self.send_response(500)
            self.send_header('X-Error-Message', sys.exc_info()[1])
            self.end_headers()


if __name__ == '__main__':
    global token, config
    # {"username": "zabbix", "password": "pass", "endpoint": "https://napp.local"}
    with open(os.getenv('SECRET', '/run/secrets/napp.json'), 'r') as f:
        config = json.load(f)
    drop_privileges()
    signal.signal(signal.SIGINT, exit_handler)
    token = get_token(config)

    port = int(os.getenv('PORT', 8080))
    server = TServer(('', port), HTTPHandler)
    print "Serving on: {}, proxy to: {}".format(port, config['endpoint'])
    server.serve_forever()
