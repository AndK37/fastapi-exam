from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/courseslessons', tags=['CoursesLessons'])
auth_handler = AuthHandler()

models_entity = models.CourseLesson
pyd_base = pyd.CourseLessonSchema
pyd_create = pyd.CreateCourseLesson

message_404 = 'Урок курса не найден'
message_404_many = 'Уроки курса не найдены'
message_already_exists = 'Урок курса уже существует'
def delete_message(name):
    return f'Урок курса \'{name}\' удален'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    
    return {'id': user_db.id, 'role_id': user_db.role_id}



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


@router.get('/{entity_id}/all', response_model=List[pyd_base])
def get_all_course_lessons(entity_id: int, db: Session=Depends(get_db)):
    entities = db.query(models_entity).filter(models_entity.id == entity_id).all()

    if not entities:
        raise HTTPException(404, message_404_many)

    return entities


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    course = db.query(models.Course).filter(models.Course.id == entity.course_id).first()
    if course.user_id != user_data['id'] and user_data['role_id'] != 3:
        raise HTTPException(403, 'Доступ запрещен')
    
    if db.query(models_entity).filter(models_entity.lesson_id == entity.lesson_id, models_entity.course_id == entity.course_id).first():
        raise HTTPException(400, message_already_exists)
    
    entity_db = models_entity()
    entity_db.course_id = entity.course_id
    entity_db.lesson_id = entity.lesson_id

    db.add(entity_db)
    db.commit()

    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    course = db.query(models.Course).filter(models.Course.id == entity.course_id).first()
    if course.user_id != user_data['id'] and user_data['role_id'] != 3:
        raise HTTPException(403, 'Доступ запрещен')

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.course_id = entity.course_id
    entity_db.lesson_id = entity.lesson_id

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    user_data = auth(jwt, db)
    course = db.query(models.Course).filter(models.Course.id == entity_db.course_id).first()
    if course.user_id != user_data['id'] and user_data['role_id'] != 3:
        raise HTTPException(403, 'Доступ запрещен')

    db.delete(entity_db)
    db.commit()

    return {'message': delete_message(entity_db.name)}