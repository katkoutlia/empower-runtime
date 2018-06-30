#!/usr/bin/env python3
#
# Copyright (c) 2016 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""IBN Protocol Server."""

import tornado.web
import tornado.ioloop
import tornado.websocket

from empower.restserver.restserver import RESTServer
from empower.ibnp.ibnpmainhandler import IBNPMainHandler

from empower.main import RUNTIME


DEFAULT_PORT = 4444


class IBNPServer(tornado.web.Application):
    """Exposes the EmPOWER IBN API."""

    handlers = [IBNPMainHandler]

    def __init__(self, port):

        self.connection = None

        self.port = port
        self.period = None
        self.last_seen = None
        self.last_seen_ts = None

        self.__seq = 0

        handlers = []

        for handler in self.handlers:
            for url in handler.HANDLERS:
                handlers.append((url, handler, dict(server=self)))

        tornado.web.Application.__init__(self, handlers)
        http_server = tornado.httpserver.HTTPServer(self)
        http_server.listen(self.port)

    @property
    def seq(self):
        """Return new sequence id."""

        self.__seq += 1
        return self.__seq


def launch(port=DEFAULT_PORT):
    """Start IBNP Server Module. """

    server = IBNPServer(int(port))
    return server