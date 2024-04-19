# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import datetime, date

from app.app import db
from sqlalchemy.exc import SQLAlchemyError


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def save(self, _commit=True, update=False):
        """保存改动，成功返回id，失败返回None"""
        try:
            if not update:
                db.session.add(self)
            if _commit:
                db.session.commit()
            return self
        except SQLAlchemyError:
            logging.error(traceback.format_exc())
            db.session.rollback()
        # finally:
        #     db.session.close()

    @classmethod
    def create(cls, _commit=True, **kwargs):
        for k in kwargs.keys():
            if not hasattr(cls, k):
                kwargs.pop(k)
        obj = cls(**kwargs)
        obj = cls.save(obj, _commit=_commit)
        return obj

    def update(self, _commit=True, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        instance = self.save(_commit=_commit, update=True)
        return instance

    @classmethod
    def get(cls, id, exclude_deleted=True):
        query = db.session.query(cls)
        if hasattr(cls, "is_delete") and exclude_deleted:
            query = query.filter_by(is_delete=0)
        return query.filter_by(id=id).first()
    
    @classmethod
    def get_with_kwargs(cls, **kwargs):
        return db.session.query(cls).filter_by(is_delete=0, **kwargs)

    @classmethod
    def list(cls, exclude_deleted=True):
        query = db.session.query(cls)
        if hasattr(cls, "is_delete") and exclude_deleted:
            query = query.filter_by(is_delete=0)
        return query

    def delete(self, _hard=True, _commit=True):
        if hasattr(self, "is_delete") and _hard is False:
            self.is_delete = 1
            self.update(update=True)
        else:
            db.session.delete(self)
        if _commit:
            db.session.commit()

    @classmethod
    def page(cls, query, page_no, page_size):
        query = query.order_by(db.desc(cls.updated_time)).paginate(page_no, per_page=page_size, error_out=False)
        return query

    def to_dict(self, fields=None, date_to_str=True):
        """将model转化为dict
        :param fields: 要取出的字段
        :param date_to_str: 是否将日期转化为字符串，格式为2017-05-05 11:11:11
        :return: dict
        usage:
            project = Project.query.filter_by(id=1).first()
            project.to_dict() or project.to_dict(["id", "name", "age"])
        """
        def convert_date(value):
            if date_to_str:
                return value if not isinstance(value, (datetime, date)) else str(value)
            else:
                return value

        if not fields:
            return {
                col: convert_date(getattr(self, col, None))
                for col in self.__table__.columns.keys()
            }
        else:
            return {key: convert_date(getattr(self, key, None)) for key in fields if not key.startswith('__')}
