# -*- coding: utf-8 -*-
import logging
import signal

from apscheduler.schedulers.background import BackgroundScheduler

from batch.logConfig import setup_logging
from scrapy.FundationGrowShedule import scrapAndSaveFinMsg

LOGGER = logging.getLogger(__name__)

_schedual = ""

def start_apshedule():

    sched = BackgroundScheduler(daemonic=False)
    sched._logger = LOGGER
    # sched.add_job(func=scrapAndSaveFinMsg, replace_existing=True, misfire_grace_time=3,
    #               trigger='cron', name='基金查询_预估值', id='scrap_fin', seconds='0/30', hour='9-15', day_of_week='0-4')

    sched.add_job(func=scrapAndSaveFinMsg, replace_existing=True, misfire_grace_time=3,
                  trigger='cron', name='基金查询_预估值_test', id='scrap_fin', second='0/30')

    #
    # sched.add_job(func=scrapAndSenFinMsg, args=[nickNames], replace_existing=True, misfire_grace_time=3,
    #               trigger='cron', name='基金查询_测试', id='scrap_fin_test', minute='0/2')
    sched.start()
    global _schedual
    _schedual = sched


def stop_apshedule():
    if isinstance(_schedual,str):
        pass
    else:
        _schedual.shutdown()




def outProgramm(signo, frame):
    global is_running
    is_running = False
    stop_apshedule()
    print("sys exit")
    pass


if __name__ == '__main__':
    is_running = True
    signal.signal(signal.SIGINT, outProgramm)
    signal.signal(signal.SIGTERM, outProgramm)

    setup_logging()
    LOGGER.info("批处理任务，启动成功！")

    start_apshedule()
    while is_running:
        pass
