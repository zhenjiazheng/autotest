# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.app import create_app, db

if __name__ == "__main__":
    app = create_app("dev")
    manager = Manager(app=app)
    migrate = Migrate(app=app, db=db)
    from app.dbs.common import *
    manager.add_command('db', MigrateCommand)
    manager.run()
