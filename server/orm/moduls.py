# -*- coding: utf-8 -*-
from pickle import FLOAT

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

mysql_conn = "mysql+pymysql://yanghuang:19951015@47.96.30.206:3306/FDT?charset=utf8"

engine = create_engine(mysql_conn, max_overflow=10, pool_size=5, pool_recycle=360, echo=True)
DB_Session = sessionmaker(bind=engine)

# 生成一个SqlORM 基类
Base = declarative_base()

def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

Base.to_dict = to_dict

# 构造ORM的
class FundationObject(Base):
    __tablename__ = 'fundation'
    fun_code = Column(String(10), primary_key=True)
    fun_name = Column(String(200))
    acc_grow = Column(String(11))
    acc_grow_int = Column(String(11))
    predict_grow = Column(String(11))
    predict_grow_int = Column(String(11))

    def setTDColor(self):
        if '-' in self.predict_grow:
           return 'green'
        else:
            return 'red'

    def setTMLColor(self):
        if '-' in self.acc_grow:
           return 'green'
        else:
            return 'red'


class SubFund(Base):
    __tablename__ = 'sub_fund'
    uuid = Column(String(36), primary_key=True)
    usr_id = Column(String(36))
    fund_id = Column(String(10))


