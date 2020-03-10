from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from .. import app
import traceback

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
Base = declarative_base()
print("DB_CREATOR")


class Client(Base):
    """"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email_address = Column(String)

    client_reports = relationship("Report", back_populates="client")
    # backref=db.backref("reports", order_by=id),


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    report_date = Column(Date)
    value_date = Column(Date)
    report_path = Column(String)
    email_status = Column(Boolean)
    balance = Column(Float)
    time = Column(DateTime)
    is_return_report = Column(Boolean)

    def __repr__(self):
        return "<Report: {}>".format(self.name)

    # client = relationship("Report", backref=backref("reports", order_by=id))
    # artist_id = Column(Integer, ForeignKey("clients.id"))

    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="client_reports")


# create tables
Base.metadata.create_all(engine)
print("I have been called {}".format(__name__))
traceback.print_stack()



