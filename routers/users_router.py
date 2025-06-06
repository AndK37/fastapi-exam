from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/users', tags=['Users'])
auth_handler = AuthHandler()



@router.post('/login')
def login(user: pyd.UserLogin, db: Session=Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.email).first()

    if not user_db:
        raise HTTPException(404, "Пользователь не найден")

    if auth_handler.verify_password(user.password, user_db.password_hash):
        token = auth_handler.encode_token(user_db.email)
        return {'token': token}
    else:
        raise HTTPException(401, 'Неправильный пароль')
    

