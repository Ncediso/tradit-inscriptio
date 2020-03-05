from .. import db


class Client(db.Model):
    """"""
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email_address = db.Column(db.String)


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    report_date = db.Column(db.Date)
    value_date = db.Column(db.Date)
    report_path = db.Column(db.String)
    email_status = db.Column(db.Boolean)
    balance = db.Column(db.Float)

    def __repr__(self):
        return "<Report: {}>".format(self.name)

    client = db.relationship("Report", backref=db.backref("reports", order_by=id))
    artist_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

