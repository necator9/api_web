from web_api_sl import db
from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy.sql import func


class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime, onupdate=func.now())
    name = db.Column(db.String(140))
    app_status = db.Column(db.Boolean)
    latitude = db.Column(db.Float)

    def __repr__(self):
        return 'Node: {}, app status: {}'.format(self.name, self.app_status)

    def object_as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
