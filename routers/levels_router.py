from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/levels', tags=['Levels'])
auth_handler = AuthHandler()

models_entity = models.Level
pyd_base = pyd.BaseLevel
pyd_create = pyd.CreateLevel

message_404 = 'Сложность не найдена'
message_404_many = 'Сложности не найдены'
message_already_exists = 'Сложность уже существует'
def delete_message(name):
    return f'Сложность \'{name}\' удалена'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')



@router.get('/', response_model=List[pyd_base])
def get_all_entities(db: Session=Depends(get_db)):
    entities = db.query(models_entity).all()

    if not entities:
        raise HTTPException(404, message_404_many)

    return entities


@router.get('/{entity_id}', response_model=pyd_base)
def get_entity(entity_id: int, db: Session=Depends(get_db)):
    entity = db.query(models_entity).filter(models_entity.id == entity_id).first()

    if not entity:
        raise HTTPException(404, message_404)

    return entity


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(jwt, db)

    if db.query(models_entity).filter(models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    entity_db.name = entity.name

    db.add(entity_db)
    db.commit()

    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.name = entity.name

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    db.delete(entity_db)
    db.commit()

    return {'message': delete_message(entity_db.name)}