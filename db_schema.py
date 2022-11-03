from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import BigInteger
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine("postgresql://marat:5051@localhost/faces_db")

Base = declarative_base()

class Users(Base):
    __tablename__ = "messages"

    id = Column(String(255), primary_key=True)
    img_target = Column(String(255))
    img_res = Column(String(255)) 
    img_result = Column(String(255)) 

    def __repr__(self):
        return f"Messages(id={self.id!r}, target={self.img_target!r}, group_id={self.img_res!r}, img_result={self.img_result!r})"


Base.metadata.create_all(engine)