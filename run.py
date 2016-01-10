#!/usr/bin/python3

#
# This is an example deployment with Tornado. (http://www.tornadoweb.org/)
#
# This script was taken from http://flask.pocoo.org/docs/0.10/deploying/wsgi-standalone/
# and slightly modiefied.
#

import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from main import app

if len(sys.argv) == 1:
	port = 80
else:
	port = sys.argv[1]

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(port)
IOLoop.instance().start()