from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/coursesrecords', tags=['CoursesRecords'])
auth_handler = AuthHandler()

models_entity = models.CourseRecord
pyd_base = pyd.CourseRecordSchema
pyd_create = pyd.CreateCourseRecord

message_404 = 'Запись на курса не найдена'
message_404_many = 'Записи на курс не найдены'
message_already_exists = 'Запись на курс уже существует'
def delete_message(name):
    return f'Запись на курс \'{name}\' удалена'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    
    return {'id': user_db.id, 'role_id': user_db.role_id}



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
        raise HTTPException(403, 'Доступ запрещен') 

    entity = db.query(models_entity).filter(models_entity.id == entity_id).first()
    
    if entity.user_id != user_data['id']:
        raise HTTPException(403, 'Доступ запрещен')

    if not entity:
        raise HTTPException(404, message_404)

    return entity


@router.get('/{user_id}/all', response_model=List[pyd_base])
def get_all_user_courses_records(user_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != user_id:
            raise HTTPException(403, 'Доступ запрещен') 
    
    entities = db.query(models_entity).filter(models_entity.user_id == user_id).all()

    if not entities:
        raise HTTPException(404, message_404_many)
    
    return entities


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    if db.query(models_entity).filter(models_entity.user_id == entity.user_id, models_entity.course_id == entity.course_id).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    entity_db.user_id = entity.user_id
    entity_db.course_id = entity.course_id

    db.add(entity_db)
    db.commit()

    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.user_id = entity.user_id
    entity_db.course_id = entity.course_id

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != entity_db.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    db.delete(entity_db)
    db.commit()

    return {'message': delete_message(entity_db.name)}