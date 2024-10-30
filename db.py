from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    price = Column(Integer)
    quantity = Column(Integer)

class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer)


engine = create_engine('sqlite:///database.db')

Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(engine)