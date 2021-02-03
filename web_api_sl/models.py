from web_api_sl import db


class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    app_status = db.Column(db.Boolean)
    latitude = db.Column(db.Float)

    def __repr__(self):
        return 'Node: {}, app status: {}'.format(self.name, self.app_status)