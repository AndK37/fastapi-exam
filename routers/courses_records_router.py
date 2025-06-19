from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler
from log import Logger



router = APIRouter(prefix='/api/coursesrecords', tags=['CoursesRecords'])
auth_handler = AuthHandler()
logger = Logger()

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

def discount(course, jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    course_records = db.query(models.CourseRecord).filter(models.CourseRecord.user_id == user_db.id).count()

    if course_records == 1:
        return course.price - course.price * 0.1
    if course_records == 2:
        return course.price - course.price * 0.2
    if course_records >= 3:
        return course.price - course.price * 0.3
    
    return course.price



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
    if user_data['role_id'] == 2:
        raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] != 3:
        if user_data['id'] != entity.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    if db.query(models_entity).filter(models_entity.user_id == entity.user_id, models_entity.course_id == entity.course_id).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    entity_db.user_id = entity.user_id
    entity_db.course_id = entity.course_id
    entity_db.price = discount(db.query(models.Course).filter(models.Course.id == entity.course_id).first(), jwt, db)

    db.add(entity_db)
    db.commit()

    logger.add('INSERT', entity_db.__tablename__, entity_db)
    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd.CreateCourseRecordAdmin, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        raise HTTPException(403, 'Доступ запрещен')

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    if db.query(models_entity).filter(models_entity.user_id == entity.user_id, models_entity.course_id == entity.course_id).first():
        raise HTTPException(400, message_already_exists)
    
    entity_db.user_id = entity.user_id
    entity_db.course_id = entity.course_id
    entity_db.price = entity.price

    db.commit()

    logger.add('UPDATE', entity_db.__tablename__, entity_db)
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

    logger.add('DELETE', entity_db.__tablename__, entity_db)
    return {'message': delete_message(entity_db.id)}