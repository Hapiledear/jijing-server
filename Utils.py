# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

from sqlalchemy.ext.declarative import DeclarativeMeta

LOGGER = logging.getLogger(__name__)

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


def isTimeReFresh():
    now_time = datetime.now()
    time_9_30 = now_time.replace(hour=9, minute=30, second=00)
    time_13_00 = now_time.replace(hour=15, minute=1, second=00)
    if now_time < time_9_30 or now_time > time_13_00:
        LOGGER.info("估算时间暂未开始 now time %s " % now_time.__str__())
        return False
    else:
        return True