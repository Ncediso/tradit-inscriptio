from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import traceback

# print("I have been called {}".format(__name__))
engine = create_engine('sqlite:///kga_reporting.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from ..models import models
    Base.metadata.create_all(bind=engine)
    print("I have been called {}".format(__name__))
    traceback.print_stack()
