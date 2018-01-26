# -*- coding: utf-8 -*-
import json
import logging

import time
import tornado
from tornado import websocket, web, escape

import Utils
from server.service.FundationService import getFundPredictGrow, unSubFundation as fs_unSubFundation, \
    subFundation as fs_subFundation, checkFundSubed as fs_checkFundSubed, getFundGrowHis
from Utils import AlchemyEncoder
from server.orm.moduls import DB_Session, SubFund, FundationObject

LOGGER = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = DB_Session()
        self.res = {}

    def on_finish(self):
        self.session.close()

    def get_current_user(self):
        return self.get_secure_cookie("user")


class getFundHisInfo(BaseHandler):
    def post(self):
        usrId = self.get_argument("openId")
        fundCode = self.get_argument("code")
        fundHisDict = getFundGrowHis(fundCode)
        fundHisDict['focus'] = fs_checkFundSubed(usrId, fundCode)
        self.write(json.dumps(fundHisDict, cls=AlchemyEncoder))


class LoginHandler(BaseHandler):
    def get(self):
        if self.get_argument("openId"):
            self.set_secure_cookie("user", self.get_argument("openId"))
        else:
            self.write("用户暂未登陆")

    def post(self):
        if self.get_argument("openId"):
            self.set_secure_cookie("user", self.get_argument("openId"))
        else:
            self.write("用户暂未登陆")


class subFundation(BaseHandler):
    def get(self):
        self.post()

    # @tornado.web.authenticated
    def post(self):
        openId = self.get_argument("openId")
        fundCode = self.get_argument("code")

        query = self.session.query(SubFund).filter_by(usr_id=openId, fund_id=fundCode).first()
        if query is not None:
            return
        fs_subFundation(openId, fundCode)
        self.res["code"] = 0
        self.write(json.dumps(self.res, cls=AlchemyEncoder))


class unsubFundation(BaseHandler):
    def get(self):
        self.post()

    # @tornado.web.authenticated
    def post(self):
        openId = self.get_argument("openId")
        fundCode = self.get_argument("code")

        query = self.session.query(SubFund).filter_by(usr_id=openId, fund_id=fundCode).first()
        if query is None:
            return

        fs_unSubFundation(openId, fundCode)
        self.res["code"] = 0
        self.write(json.dumps(self.res, cls=AlchemyEncoder))


class getSubFundation(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        self.post()

    # @tornado.web.authenticated
    def post(self):
        res = {}
        res['refresh'] = Utils.isTimeReFresh()
        resList = []
        # openId = escape.xhtml_escape(self.current_user)
        openId = self.get_argument("openId")
        query = self.session.query(SubFund)
        sub_list = query.filter(SubFund.usr_id == openId).all()
        for subFund in sub_list:
            d_fund = {}
            fundInfo = self.session.query(FundationObject). \
                filter_by(fun_code=subFund.fund_id).first()
            d_fund['fCode'] = fundInfo.fun_code
            d_fund['fName'] = fundInfo.fun_name
            d_fund['tday_num'] = fundInfo.predict_grow
            d_fund['tday_deg'] = fundInfo.predict_grow_int
            d_fund['today_color'] = fundInfo.setTDColor()

            d_fund['tml_num'] = fundInfo.acc_grow
            d_fund['tml_deg'] = fundInfo.acc_grow_int
            d_fund['tml_color'] = fundInfo.setTMLColor()
            resList.append(d_fund)
        self.session.commit()
        res['resList'] = resList

        LOGGER.info("返回值= %s " % json.dumps(res, cls=AlchemyEncoder))
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(res, cls=AlchemyEncoder))


class IndexHandler(BaseHandler):
    def get(self):
        self.render("../resources/index.html")


class FundPredGrowWebSocket(websocket.WebSocketHandler):
    def open(self):
        LOGGER.info("WebSocket opened")

    def on_message(self, message):
        # todo 这里写定时任务 定时推送消息 接收到id后
        fundList = message.split("|")
        while True:
            resList = []
            for fundCode in fundList:
                resList.append(getFundPredictGrow(fundCode))
            self.write_message(json.dumps(resList))
            time.sleep(30)

    def on_close(self):
        LOGGER.info("WebSocket closed")
