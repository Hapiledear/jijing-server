# -*- coding: utf-8 -*-
import logging
import signal

import os
from tornado import web, ioloop, httpserver

from server.controller.WebSocket import *
from server.logConfig import setup_logging

LOGGER = logging.getLogger(__name__)

settings = {
    "cookie_secret": "oE_gI0QCgqZv6fMf4lEENhJIS2Xk",
    "login_url": "/login",
}
app = web.Application([
    (r'/', IndexHandler),
    (r'/login', LoginHandler),
    (r'/subList',getSubFundation),
    (r'/sub', subFundation),
    (r'/unSub', unsubFundation),
    (r'/fundHis', getFundHisInfo),
    (r'/fpg', FundPredGrowWebSocket),
], **settings)


def outProgramm(signo, frame):
    global is_running
    is_running = False
    ioloop.IOLoop.instance().stop()
    print("sys exit")
    pass


if __name__ == '__main__':
    is_running = True
    signal.signal(signal.SIGINT, outProgramm)
    signal.signal(signal.SIGTERM, outProgramm)

    setup_logging()
    LOGGER.info("websocket任务，启动成功！")
    app.listen(8888)
    ioloop.IOLoop.instance().start()
    while is_running:
        pass
