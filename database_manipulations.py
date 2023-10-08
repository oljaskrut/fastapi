from sqlalchemy import create_engine, Column, Integer,  ForeignKey, Text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as ORMSession
from sqlalchemy.ext.declarative import declarative_base



metadata = MetaData()
Base = declarative_base()
engine = create_engine('sqlite:///database.db')

def get_db_session() -> ORMSession:
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)() #здесь мы создаем фабрику сессий 


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    
    
    @classmethod 
    def find_user(cls, tg_id, session=get_db_session()):
        user = session.query(cls).filter_by(user_id= tg_id)
        if user:
            return user
        
    
    @classmethod
    def check_user_exist(cls: ORMSession, user_id, session=get_db_session()):
        query = session.query(cls).filter_by(user_id=user_id).first()
        #user_attributes = vars(user)
        return query is not None 
    
    
    @classmethod
    def add_user(cls, tg_id: int, session=get_db_session()) -> bool:
        user = session.query(cls).filter_by(user_id=tg_id).first()
        if not user:
            new_user = Users(user_id=tg_id)
            session.add(new_user)
            session.commit()
            return True
        
        
class Chat(Base):
    __tablename__ = 'chat'
    msg_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    question = Column(Text(500))
    answer = Column(Text(1000))
    point = Column(Integer)
    
    
    @classmethod 
    def insert_to_chat(cls, user_id, question, answer, session=get_db_session()):
        new_message = Chat(user_id=user_id, question=question, answer=answer)
        session.add(new_message)
        session.commit()
    
    

def initialize_database():
    Base.metadata.create_all(engine)
    
if __name__ == "__main__":
    initialize_database()