# -*- coding: utf-8 -*-
import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from server.orm.moduls import engine, FundationObject, SubFund

LOGGER = logging.getLogger(__name__)


# true 用户以订阅该基金
def checkFundSubed(usrId, fundCode):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        res = session.query(SubFund).filter_by(usr_id=usrId, fund_id=fundCode).first()
        return res is not None
    finally:
        session.commit()
        session.close()


def getFundGrowHis(fundCode):
    from scrapy.FundationGrowShedule import collectFundationHis
    return collectFundationHis(fundCode)



def getFundPredictGrow(fundCode):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        d_res = {}
        res = session.query(FundationObject). \
            filter_by(fun_code=fundCode).first()
        d_res['tday_num'] = res.predict_grow
        d_res['tday_deg'] = res.predict_grow_int
        d_res['today_color'] = res.setTDColor()
        return d_res
    finally:
        session.expunge_all()
        session.commit()
        session.close()


def getFundList():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        res = session.query(FundationObject).all()
        return res
    finally:
        session.expunge_all()
        session.commit()
        session.close()


def updPredictGrow(fundObj):
    if isinstance(fundObj, FundationObject):
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.query(FundationObject).with_lockmode('update'). \
                filter(FundationObject.fun_code == fundObj.fun_code). \
                update({FundationObject.predict_grow: fundObj.predict_grow})
        finally:
            session.commit()
            session.close()
    else:
        LOGGER.warning("%s 不是FundationObject" % fundObj.__dict__)


def subFundation(usrId, fundCode):
    sub_fund = SubFund()
    sub_fund.uuid = uuid.uuid1().__str__()
    sub_fund.usr_id = usrId
    sub_fund.fund_id = fundCode

    from scrapy.FundationGrowShedule import collectFundation

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        session.add(sub_fund)
        query = session.query(FundationObject).filter_by(fun_code=fundCode).first()
        if query is None:
            fundInfo = collectFundation(fundCode)
            session.add(fundInfo)
    finally:
        session.commit()
        session.close()


def unSubFundation(usrId, fundCode):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        unsub_fund = session.query(SubFund).filter_by(usr_id=usrId, fund_id=fundCode).first()
        session.delete(unsub_fund)
    finally:
        session.commit()
        session.close()
