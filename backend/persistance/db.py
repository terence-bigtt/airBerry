from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

Base = declarative_base()


class Connector(object):
    def __init__(self, dburl=None, env=None, echo=False):
        self.dburl = dburl
        self.echo = echo
        self.engine = None
        self.sessionmaker = None
        self.session = None
        self.init()

    def init(self):
        self.engine = create_engine(self.dburl, echo=self.echo)
        self.sessionmaker = sessionmaker(bind=self.engine)
        self.session = self.sessionmaker()

    def create_schema(self):
        Base.metadata.create_all(bind=self.engine)

    def insert_if_not_exists(self, obj):
        Klass = type(obj)
        session = self.session
        q = session.query(Klass)
        exists = session.query(q.filter(Klass.id == obj.id).exists()).scalar()
        if not exists:
            session.add(obj)
            session.commit()

    def get(self, obj):
        Klass = type(obj)
        session = self.session
        q = session.query(Klass).filter(Klass.id == obj.id).all()
        if len(q) != 0:
            return q[0]

    def truncate(self, table_name):
        engine = self.engine
        meta = MetaData(bind=engine, reflect=True)
        con = engine.connect()
        trans = con.begin()
        for table in meta.sorted_tables:
            if table.name == table_name:
                con.execute(table.delete())
        trans.commit()

    def get_all(self, Klass):
        session = self.session
        q = session.query(Klass).all()
        if len(q) != 0:
            return q
