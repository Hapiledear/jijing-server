# -*- coding: utf-8 -*-
import json
import logging
import re
import time as tm
from datetime import datetime

import requests

import Utils
from server.orm.moduls import FundationObject

LOGGER = logging.getLogger(__name__)

re_stock_code = r'(?<=\.com\/).*(?=\.html)'
re_get_json = r'{.*}'

start_url = "http://fund.eastmoney.com/{0}.html?spm=search"
fund_pred_url = "http://fundgz.1234567.com.cn/js/{0}.js?rt={1}"

# 类中属性为类的所有实例共有
session = requests.Session()
header_info = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

session.headers.update(header_info)


def scrapAndSaveFinMsg():
    if not Utils.isTimeReFresh():
        return

    from server.service import FundationService
    from FundationService import getFundList
    fList = getFundList()
    for f in fList:
        reqUrl = fund_pred_url.format(f.fun_code, tm.time())
        LOGGER.debug("请求url=%s " % reqUrl)
        response = session.get(reqUrl)  # get请求方式，并设置请求头
        resJsonStr = re.findall(re_get_json, response.text)[0]
        resJson = json.loads(resJsonStr)

        fundObj = FundationObject()
        fundObj.fun_code = f.fun_code
        fundObj.predict_grow = resJson['gszzl'] + "%"
        fundObj.predict_grow_int = resJson['gsz']
        FundationService.updPredictGrow(fundObj)
    pass


def collectFundation(fundCode):
    reqUrl = start_url.format(fundCode)
    LOGGER.debug("请求url=%s " % reqUrl)
    response = session.get(reqUrl)  # get请求方式，并设置请求头
    fundObj = parseResponse(response, fundCode)
    return fundObj


def parseResponse(response, fundCode='0000'):
    htmltext = response.text.encode(response.encoding).decode('utf-8')
    from lxml import etree
    html = etree.HTML(htmltext)
    fundName = html.xpath('//*[@id="body"]/div[9]/div/div/a[3]')[0].text
    acc_grow = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[2]/dd[1]/span[2]')[0].text
    acc_grow_int = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[2]/dd[1]/span[1]')[0].text

    predict_grow = html.xpath('//*[@id="gz_gszzl"]')[0].text
    predict_grow_int = html.xpath('//*[@id="gz_gsz"]')[0].text

    LOGGER.info("基金名称 %s " % fundName)

    fundObj = FundationObject()
    fundObj.fun_code = fundCode
    fundObj.fun_name = fundName
    fundObj.acc_grow_int = acc_grow_int
    fundObj.acc_grow = acc_grow
    fundObj.predict_grow = predict_grow
    fundObj.predict_grow_int = predict_grow_int

    return fundObj

def collectFundationHis(fundCode):
    reqUrl = start_url.format(fundCode)
    LOGGER.debug("请求url=%s " % reqUrl)
    response = session.get(reqUrl)  # get请求方式，并设置请求头
    fundObj = parseFundHis(response)
    fundObj['code'] = fundCode
    return fundObj

def parseFundHis(response):
    fundObj = {}
    htmltext = response.text.encode(response.encoding).decode('utf-8')
    from lxml import etree
    html = etree.HTML(htmltext)
    fundObj['name'] = html.xpath('//*[@id="body"]/div[9]/div/div/a[3]')[0].text
    fundObj['m1_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[1]/dd[2]/span[2]')[0].text
    fundObj['m1_color'] = setColor(fundObj['m1_deg'])

    fundObj['m3_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[2]/dd[2]/span[2]')[0].text
    fundObj['m3_color'] = setColor(fundObj['m3_deg'])

    fundObj['m6_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[3]/dd[2]/span[2]')[0].text
    fundObj['m6_color'] = setColor(fundObj['m6_deg'])

    fundObj['y1_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[1]/dd[3]/span[2]')[0].text
    fundObj['y1_color'] = setColor(fundObj['y1_deg'])

    fundObj['y3_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[2]/dd[3]/span[2]')[0].text
    fundObj['y3_color'] = setColor(fundObj['y3_deg'])

    fundObj['all_deg'] = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[3]/dd[3]/span[2]')[0].text
    fundObj['all_color'] = setColor(fundObj['all_deg'])

    return fundObj

def setColor(deg):
    if "--" == deg:
        return "black"
    elif "-" in deg:
        return "green"
    else:
        return "red"

if __name__ == '__main__':
    collectFundationHis("519772")
