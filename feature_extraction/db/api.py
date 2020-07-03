from configuration import conf
from db.models import Base
from db.models import model_from_name
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataBaseApi:
    def __init__(self):
        self.__db_name = conf.db_name
        self.__username = conf.db_username
        self.__password = conf.db_password

        engine = self.create_eng()
        #create_tables
        Base.metadata.create_all(engine)
        self.__session = sessionmaker(bind=engine)()

    def create_eng(self):
        return create_engine('mysql+mysqlconnector://%s:%s@localhost:3306/%s?charset=utf8' %
                            (self.__username, self.__password, self.__db_name))

    def close_session(self):
        self.__session.close()

    def insert_objs(self, db_objs):
        for db_obj in db_objs:
            self.__session.add(db_obj)
        self.__session.commit()

    def query_all(self, table_name):
        try:
            model = model_from_name(table_name)
            query = self.__session.query(model).all()
            return query
        except KeyError:
            return None


if __name__ == '__main__':
    DBAPI = DataBaseApi()
    db_data = DBAPI.query_all('paper')
    for db_d in db_data:
        print(db_d.title)
    DBAPI.close_session()
