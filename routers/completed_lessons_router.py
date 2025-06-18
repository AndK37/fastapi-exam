from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/completedlessons', tags=['CompletedLessons'])
auth_handler = AuthHandler()

models_entity = models.CompletedLesson
pyd_base = pyd.CompletedLessonSchema
pyd_create = pyd.CreateCompletedLesson

message_404 = 'Пройденый урок не найден'
message_404_many = 'Пройденые уроки не найдены'
message_already_exists = 'Пройденый урок уже существует'
def delete_message(name):
    return f'Пройденый урок \'{name}\' удален'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    
    return {'id': user_db.id, 'role_id': user_db.role_id}

def recalculate_progression(user_id, lesson_id, db):
    course = db.query(models.CourseLesson).filter(models.CourseLesson.lesson_id == lesson_id).first()
    completed_lessons = db.query(models.CompletedLesson).filter(models.CompletedLesson.user_id == user_id).all()
    course_lessons = db.query(models.CourseLesson).filter(models.CourseLesson.course_id == course.course_id).all()
    
    complete = 0
    for course_lesson in course_lessons:
        for completed_lesson in completed_lessons:
            if course_lesson.lesson_id == completed_lesson.lesson_id:
                complete += 1
    
    course_record = db.query(models.CourseRecord).filter(models.CourseRecord.course_id == course.course_id, models.CourseRecord.user_id == user_id).first()
    course_record.progression = round(complete / len(course_lessons), 2)

    db.commit()

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


@router.get('/{user_id}/all', response_model=List[pyd.UserCompletedLessonsSchema])
def get_all_user_completed_lessons(user_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] != 3:
        if user_data['id'] != user_id:
            raise HTTPException(403, 'Доступ запрещен')

    entities = db.query(models_entity).filter(models_entity.user_id == user_id).all()

    if not entities:
        raise HTTPException(404, message_404_many)

    return entities


@router.post('/', response_model=pyd_base)
def complete_lesson(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] == 2:
            raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] != 3:
        if user_data['id'] != entity.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    if db.query(models_entity).filter(models_entity.user_id == entity.user_id, models_entity.lesson_id == entity.lesson_id).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    entity_db.lesson_id = entity.lesson_id
    entity_db.user_id = entity.user_id

    db.add(entity_db)
    db.commit()

    recalculate_progression(user_data['id'], entity.lesson_id, db)

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
    
    entity_db.lesson_id = entity.lesson_id
    entity_db.user_id = entity.user_id

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
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