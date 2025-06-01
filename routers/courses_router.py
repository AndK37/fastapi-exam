from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/courses', tags=['Courses'])
auth_handler = AuthHandler()



@router.get('/')
def get_courses(page: int | None = Query(default=None, gt=0), 
                limit: int | None = Query(default=None, ge=0), 
                category: str | None = Query(default=None, max_length=32), 
                level: str | None = Query(default=None, max_length=32), 
                db: Session=Depends(get_db)):
    pass
    

# @router.post('/login')
# def login(user: pyd.BaseUserLogin, db: Session=Depends(get_db)):
#     user_db = db.query(models.User).filter(models.User.login == user.login).first()

#     if not user_db:
#         raise HTTPException(404, "Пользователь не найден")

#     if auth_handler.verify_password(user.password, user_db.password):
#         token = auth_handler.encode_token(user_db.login)
#         return {'token': token}
#     else:
#         raise HTTPException(403, 'Неправильный пароль')

# @router.get('/', response_model=List[pyd.UserSchema])
# def get_all_users(db: Session=Depends(get_db)):
#     users = db.query(models.User).all()

#     if not users:
#         raise HTTPException(404, "Пользователи не найдены")

#     return users


# @router.get('/', response_model=pyd.UserSchema)
# def get_user(db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
#     user_db = db.query(models.User).filter(models.User.login == jwt).first()

#     if not user_db:
#         raise HTTPException(404, "Пользователь не найден")

#     return user_db

# @router.post('/', response_model=pyd.UserSchema)
# def create_user(user: pyd.CreateUser, db: Session=Depends(get_db)):
#     user_db = models.User()
#     user_db.surname = user.surname
#     user_db.name = user.name
#     user_db.email = user.email
#     user_db.login = user.login
#     user_db.password = auth_handler.get_password_hash(user.password)
#     user_db.role_id = user.role

#     role_db  = db.query(models.Role).filter(models.Role.id == user.role).first()
#     if not role_db:
#         raise HTTPException(400, 'Неправильная роль')

#     db.add(user_db)
#     db.commit()

#     return user_db


# @router.put('/{id}/new_password', response_model=pyd.UserSchema)
# def update_user_password(id: int, new_password: str, db: Session=Depends(get_db)):
#     user_db = db.query(models.User).filter(models.User.id == id).first()
#     if not user_db:
#         raise HTTPException(404, "Пользователь не найден")
    
#     user_db.password = auth_handler.get_password_hash(new_password)

#     db.commit()

#     return user_db


# @router.put('/{id}', response_model=pyd.UserSchema)
# def update_user(id: int, user: pyd.CreateUser, db: Session=Depends(get_db)):
#     user_db = db.query(models.User).filter(models.User.id == id).first()
#     if not user_db:
#         raise HTTPException(404, "Пользователь не найден")

#     user_db.surname = user.surname
#     user_db.name = user.name
#     user_db.email = user.email
#     user_db.login = user.login
#     user_db.password = auth_handler.get_password_hash(user.password)
#     user_db.role_id = user.role

#     role_db  = db.query(models.Role).filter(models.Role.id == user.role).first()
#     if not role_db:
#         raise HTTPException(400, 'Неправильная роль')

#     db.commit()

#     return user_db


# @router.delete('/{id}')
# def delete_user(id: int, user: pyd.CreateUser, db: Session=Depends(get_db)):
#     user_db = db.query(models.User).filter(models.User.id == id).first()
#     if not user_db:
#         raise HTTPException(404, "Пользователь не найден")

#     db.delete(user_db)
#     db.commit()

#     return {'msg': 'Удалено'}

