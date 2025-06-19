from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler
from log import Logger



router = APIRouter(prefix='/api/users', tags=['Users'])
auth_handler = AuthHandler()
logger = Logger()

models_entity = models.User
pyd_base = pyd.UserSchema
pyd_create = pyd.CreateUser

message_404 = 'Пользователь не найден'
message_404_many = 'Пользователи не найдены'
message_already_exists = 'Пользователь уже существует'
def delete_message(name):
    return f'Пользователь \'{name}\' удален'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    
    return {'id': user_db.id, 'role_id': user_db.role_id}



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


@router.get('/', response_model=List[pyd_base])
def get_all_entities(db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        raise HTTPException(403, 'Доступ запрещен') 

    entities = db.query(models_entity).all()

    if not entities:
        raise HTTPException(404, message_404_many)

    return entities


@router.get('/{entity_id}', response_model=pyd_base)
def get_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity_id:
            raise HTTPException(403, 'Доступ запрещен') 

    entity = db.query(models_entity).filter(models_entity.id == entity_id).first()

    if not entity:
        raise HTTPException(404, message_404)

    return entity


@router.post('/', response_model=pyd_base)
def register(entity: pyd_create, db: Session=Depends(get_db)):
    if db.query(models_entity).filter(models_entity.email == entity.email).first():
        raise HTTPException(400, message_already_exists)
    if entity.role_id == 3:
        raise HTTPException(403, 'Доступ запрещен')
    if not db.query(models.Role).filter(models.Role.id == entity.role_id).first():
        raise HTTPException(404, 'Роль не существует')

    entity_db = models_entity()
    entity_db.surname = entity.surname
    entity_db.name = entity.name
    entity_db.email = entity.email
    entity_db.password_hash = auth_handler.get_password_hash(entity.password)
    entity_db.role_id = entity.role_id

    db.add(entity_db)
    db.commit()

    logger.add('INSERT', entity_db.__tablename__, entity_db)
    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd.UpdateUser, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity_id:
            raise HTTPException(403, 'Доступ запрещен') 
    
    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.surname = entity.surname
    entity_db.name = entity.name
    entity_db.password_hash = auth_handler.get_password_hash(entity.password)

    db.commit()

    logger.add('UPDATE', entity_db.__tablename__, entity_db)
    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity_id:
            raise HTTPException(403, 'Доступ запрещен') 

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    db.delete(entity_db)
    db.commit()

    logger.add('DELETE', entity_db.__tablename__, entity_db)
    return {'message': delete_message(entity_db.surname + ' ' + entity_db.name)}