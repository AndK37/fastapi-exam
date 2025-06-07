from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/lessons', tags=['Lessons'])
auth_handler = AuthHandler()

models_entity = models.Lesson
pyd_base = pyd.LessonSchema
pyd_create = pyd.CreateLesson

message_404 = 'Урок не найден'
message_404_many = 'Уроки не найдены'
message_already_exists = 'Урок уже существует'
def delete_message(name):
    return f'Урок \'{name}\' удален'

def auth(entity_id, jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')
    
    lesson = db.query(models.Lesson).filter(models.Lesson.id == entity_id).first()
    course = db.query(models.Course).filter(models.Course.id == lesson.course_id).first()
    author = db.query(models.User).filter(models.User.id == course.author_id).first()

    if author.id != user_db.id:
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
    if db.query(models_entity).filter(models_entity.course_id == entity.course_id, models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    auth(entity_db.id, jwt, db)

    entity_db.course_id = entity.course_id
    entity_db.name = entity.name
    entity_db.video_url = entity.video_url
    entity_db.duration = entity.duration
    entity_db.order = entity.order

    db.add(entity_db)
    db.commit()

    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(entity_id, jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.course_id = entity.course_id
    entity_db.name = entity.name
    entity_db.video_url = entity.video_url
    entity_db.duration = entity.duration
    entity_db.order = entity.order

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    auth(entity_id, jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    db.delete(entity_db)
    db.commit()

    return {'message': delete_message(entity_db.name)}