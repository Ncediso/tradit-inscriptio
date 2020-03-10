from .. import db
from datetime import datetime
from ..compat import basestring
from flask import current_app, url_for
from ..app_utils.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    def __init__(self):
        """"""
        self.update_time = None
        self.create_time = None

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        instance.create_time = datetime.now()
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.update_time = datetime.now()
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class FunctionsMixin(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, basestring) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None

    def pp(self):
        """"""
        print("{}".format(self.__class__.__name__))
        for item, value in self.__dict__.items():
            print("  {}: {}".format(item, value))
        print("\n")


class Model(CRUDMixin, FunctionsMixin, db.Model):
    """Base model class that includes CRUD and Pretty Print convenience methods."""
    __abstract__ = True


class Client(Model):
    """"""
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email_address = db.Column(db.String)

    client_reports = db.relationship("Report", back_populates="client")
    # backref=db.backref("reports", order_by=id),

    def __repr__(self):
        return "<Client: {}>".format(self.name)

    # def __init__(self, name, email):
    #     pass


class Report(Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    report_date = db.Column(db.Date)
    value_date = db.Column(db.Date)
    report_path = db.Column(db.String)
    email_status = db.Column(db.Boolean)
    time = db.Column(db.DateTime)
    is_return_report = db.Column(db.Boolean)

    def __repr__(self):
        return "<Report: {}>".format(self.name)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    client = db.relationship("Client", back_populates="client_reports")
