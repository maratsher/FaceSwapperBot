from tokenize import group
from db_schema import Base, Users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://marat:5051@localhost/faces_db")

session = sessionmaker(bind=engine)
s = session()

def update_img(id, column:str, img:str):
    table = s.query(Users).filter(Users.id == id)
    table.update({column:img},
                    synchronize_session='fetch')
    s.commit()

def add_user(id):
    if (s.query(Users).filter(Users.id == id).count()):
        return
    
    user = Users(
        id = id,
        img_target = None,
        img_res = None,
        img_result = None
    )
    s.add(user)
    s.commit()

def get_target_img(id):
    user  = s.query(Users).filter_by(id=id).first()
    print(user)
    return user.img_target