from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///kga_reporting.db', echo=True)
Base = declarative_base()


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    report_date = Column(Date)
    value_date = Column(Date)
    report_path = Column(String)
    email_status = Column(Boolean)
    balance = Column(Float)

    def __repr__(self):
        return "<Report: {}>".format(self.name)

    client = relationship("Report", backref=backref(
        "reports", order_by=id))
    artist_id = Column(Integer, ForeignKey("clients.id"))


class Client(Base):
    """"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email_address = Column(String)


# create tables
Base.metadata.create_all(engine)
