# -*- coding: utf-8 -*-
from .base import *
from sqlalchemy import Table, Column, MetaData, Integer, Computed

metadata = MetaData()


class WorkItems(Base):
    __tablename__ = 'work_items'
    project_id = db.Column(db.Integer, nullable=False, comment="归属项目")
    version_id = db.Column(db.Integer, nullable=True, comment="版本")
    sprint_id = db.Column(db.Integer, nullable=True, comment="迭代")
    title = db.Column(db.String(255), unique=True)
    update_title = db.Column(db.String(255), unique=True, nullable=True, comment="项目内修改标题")
    type = db.Column(db.Integer, nullable=True, default=1, comment='1: 需求 2: 缺陷 3: 任务')
    content = db.Column(db.String(2048), nullable=True)
    attach = db.Column(db.String(128), nullable=True)
    level = db.Column(db.Integer, nullable=True, default=1, comment='1: 开放 2: 保密 3: 项目共享')
    creator = db.Column(db.String(32), nullable=False)
    owner = db.Column(db.String(32), nullable=True)
    status = db.Column(db.Integer, nullable=True, default=1, comment="1: 新建， 2:已规划版本，3:规划迭代  4:进行中 5: 完成")
    relateds = db.Column(db.JSON, nullable=True, default={}, comment="关联内容，关联wiki，关联测试用例，关联代码commitid")
    workload = db.Column(db.Integer, nullable=True, default=0, comment="工作量 人/天")
    plan_start = db.Column(db.DateTime, default=None)
    plan_end = db.Column(db.DateTime, default=None)
    progress = db.Column(db.String(128), nullable=False)
    follower= db.Column(db.JSON, nullable=True, default=[], nullable=True)
    sub_items = db.Column(db.JSON, nullable=True, default=[], comment="子工作项列表")
    is_delete = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, project_id, title, update_title, type=1, content='', version_id=None, sprint_id=None, attach='', level=1, creator=0, owner=0, status=0, 
                 relateds={}, workload=0, plan_start=None, plan_end=None, progress=None, follower=[], sub_items=[], is_delete=0):
        self.project_id = project_id
        self.title = title
        self.update_title = update_title
        self.type = type
        self.content = content
        self.version_id = version_id
        self.sprint_id = sprint_id
        self.attach = attach
        self.level = level
        self.creator = creator
        self.owner = owner
        self.status = status
        self.relateds = relateds
        self.workload = workload
        self.plan_start = plan_start
        self.plan_end = plan_end
        self.progress = progress
        self.follower = follower
        self.sub_items = sub_items
        self.sprint_id = sprint_id
        self.is_delete = is_delete

    def __repr__(self):
        return '<Id: %r>' % self.id
