from web_api_sl import db
from sqlalchemy import inspect
from sqlalchemy.sql import func


class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime, onupdate=func.now())
    name = db.Column(db.String(140))
    app_status = db.Column(db.Boolean)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    lamp_shutdown_interval = db.Column(db.Float)
    bright_lvl = db.Column(db.Integer)
    dimm_lvl = db.Column(db.Integer)
    max_obj_speed = db.Column(db.Float)
    min_obj_speed = db.Column(db.Float)
    max_neighbour_distance = db.Column(db.Float)
    light_distance = db.Column(db.Float)
    toler_angles = db.Column(db.Float)

    def __repr__(self):
        return 'Node: {}, app status: {}'.format(self.name, self.app_status)

    def object_as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
