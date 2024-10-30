from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
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


def init_items():
    """Инициализация таблицы товаров начальными данными."""
    with session_scope() as session:
        # Проверяем, есть ли уже записи в таблице
        if session.query(Items).first() is None:
            # Список товаров для инициализации
            initial_items = [
                Items(name="Ноутбук HP", price=45000, quantity=10),
                Items(name="Смартфон Samsung", price=25000, quantity=15),
                Items(name="Планшет iPad", price=35000, quantity=8),
                Items(name="Наушники Sony", price=8000, quantity=20),
                Items(name="Умные часы Apple Watch", price=30000, quantity=12),
                Items(name="Фотоаппарат Canon", price=40000, quantity=5),
                Items(name="Игровая приставка PlayStation", price=50000, quantity=7),
                Items(name="Электронная книга Kindle", price=12000, quantity=15),
                Items(name="Портативная колонка JBL", price=7000, quantity=25),
                Items(name="Монитор Dell", price=20000, quantity=10)
            ]
            # Добавляем товары в базу
            session.add_all(initial_items)
            print("База данных инициализирована начальными товарами")
        else:
            print("База данных уже содержит товары, пропускаем инициализацию")


def init_db():
    """Инициализация базы данных и заполнение начальными данными."""
    Base.metadata.create_all(engine)
    init_items()