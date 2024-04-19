# -*- coding: utf-8 -*-
from .base import *
from sqlalchemy import Table, Column, MetaData, Integer, Computed

metadata = MetaData()


class Users(Base):
    __tablename__ = 'users'
    account = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(64), unique=True)
    mobile = db.Column(db.String(32), nullable=True)
    password = db.Column(db.String(1024), nullable=False)
    role_id = db.Column(db.Integer, nullable=True, default=3, comment="1: Admin, 2: Project Admin, 3: Common User")
    menu_ids = db.Column(db.JSON, nullable=True, default=[], comment="页面访问权限")
    accces_apis = db.Column(db.JSON, nullable=True, default=[], comment="接口访问权限")
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, account, username, password, mobile=None, role_id=3, menu_ids=[], accces_apis=[], is_delete=0):
        self.account = account
        self.username = username
        self.password = password
        self.mobile = mobile
        self.role_id = role_id
        self.menu_ids = menu_ids
        self.accces_apis = accces_apis
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id



class Project(Base):
    __tablename__ = 'projects'
    name = db.Column(db.String(255), unique=False)
    description = db.Column(db.String(1024))
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, name, description, is_delete=0):
        self.name = name
        self.description = description
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id


class Versions(Base):
    __tablename__ = 'versions'
    name = db.Column(db.String(255), unique=False)
    description = db.Column(db.String(1024))
    report = db.Column(db.String(1024))
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, name, description, report=None, is_delete=0):
        self.name = name
        self.description = description
        self.report = report
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id


class Sprints(Base):
    __tablename__ = 'sprints'
    name = db.Column(db.String(255), unique=False)
    description = db.Column(db.String(1024))
    report = db.Column(db.String(1024))
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, name, description, report=None, is_delete=0):
        self.name = name
        self.description = description
        self.report = report
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id
    

class Tasks(Base):
    __tablename__ = 'tasks'
    project_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(80), nullable=False)
    env = db.Column(db.JSON, comment="env参数变量")
    mark = db.Column(db.String(80))
    vol = db.Column(db.JSON, comment="挂载参数")
    pipeline_id = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, default=1, comment="1: running 2: finished")
    result = db.Column(db.JSON, comment="测试结果", nullable=True)
    report = db.Column(db.String(512), nullable=True )
    command = db.Column(db.String(256), nullable=True) 
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, project_id, image, env, mark, pipeline_id, vol='{}', status=1,  result='{}', report='', command='', is_delete=0):
        self.project_id = project_id
        self.image = image
        self.env = env
        self.mark = mark
        self.vol = vol
        self.pipeline_id = pipeline_id
        self.status = status
        self.result = result
        self.report = report
        self.command = command
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id
    

class RunToolRecord(Base):
    __tablename__ = 'run_tool_records'
    type = db.Column(db.Integer, default=1, comment="1: HW_Monitor 2: tobe add")
    params = db.Column(db.JSON, comment="工具参数")

    def __init__(self, type, params):
        self.type = type
        self.params = params

    def __repr__(self):
        return '<Id: %r>' % self.id

class Reports(Base):
    __tablename__ = 'reports'
    task_id = db.Column(db.Integer, nullable=False, index=True)
    url = db.Column(db.String(1024), nullable=False)
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, task_id, url, is_delete=0):
        self.task_id = task_id
        self.url = url
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id