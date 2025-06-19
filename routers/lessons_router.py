from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler
from log import Logger
from datetime import datetime



router = APIRouter(prefix='/api/lessons', tags=['Lessons'])
auth_handler = AuthHandler()
logger = Logger()

models_entity = models.Lesson
pyd_base = pyd.LessonSchema
pyd_create = pyd.CreateLesson

message_404 = 'Урок не найден'
message_404_many = 'Уроки не найдены'
message_already_exists = 'Урок уже существует'
def delete_message(name):
    return f'Урок \'{name}\' удален'

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


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] == 1:
        raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] == 2:
        course = db.query(models.Course).filter(models.Course.id == entity.course_id).first()
        if course.user_id != user_data['id']:
            raise HTTPException(403, 'Доступ запрещен')
        
    if db.query(models_entity).filter(models_entity.course_id == entity.course_id, models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)
    if not db.query(models.Course).filter(models.Course.id == entity.course_id).first():
        raise HTTPException(404, 'Курс не существует')

    entity_db = models_entity()
    entity_db.course_id = entity.course_id
    entity_db.name = entity.name
    entity_db.duration = entity.duration
    entity_db.order = entity.order

    db.add(entity_db)
    db.commit()

    logger.add('INSERT', entity_db.__tablename__, entity_db)
    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] == 1:
        raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] == 2:
        course = db.query(models.Course).filter(models.Course.id == entity.course_id).first()
        if course.user_id != user_data['id']:
            raise HTTPException(403, 'Доступ запрещен')

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    if db.query(models_entity).filter(models_entity.course_id == entity.course_id, models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)
    if not db.query(models.Course).filter(models.Course.id == entity.course_id).first():
        raise HTTPException(404, 'Курс не существует')
    
    entity_db.course_id = entity.course_id
    entity_db.name = entity.name
    entity_db.duration = entity.duration
    entity_db.order = entity.order

    db.commit()

    logger.add('UPDATE', entity_db.__tablename__, entity_db)
    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)

    user_data = auth(jwt, db)
    if user_data['role_id'] == 1:
        raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] == 2:
        course = db.query(models.Course).filter(models.Course.id == entity_db.course_id).first()
        if course.user_id != user_data['id']:
            raise HTTPException(403, 'Доступ запрещен')

    db.delete(entity_db)
    db.commit()

    logger.add('DELETE', entity_db.__tablename__, entity_db)
    return {'message': delete_message(entity_db.name)}


@router.put('/{lesson_id}/video/', response_model=pyd.LessonSchema)
def update_lesson_video(lesson_id: int, file: UploadFile = File(...), db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    allowed_formats = ['video/mp4']

    if file.content_type not in allowed_formats:
        raise HTTPException(400, 'Неправильный формат')
    
    # if file.size > 2097152:
    #     raise HTTPException(400, 'Файл больше 2mb')
    
    file.filename = str(datetime.now().timestamp()).replace('.', '0')

    file_dir = f"./lessons/{file.filename}.{file.content_type[6:]}"
    with open(file_dir, "wb+") as file_object:
        file_object.write(file.file.read())

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()

    course = db.query(models.Course).filter(models.Course.id == lesson.course_id).first()
    user_data = auth(jwt, db)
    if user_data['role_id'] == 1:
        raise HTTPException(403, 'Доступ запрещен')
    if user_data['role_id'] != 3:
        if user_data['id'] != course.user_id:
            raise HTTPException(403, 'Доступ запрещен')

    if not lesson:
        raise HTTPException(404, "Урок не найден")
    
    lesson.video_url = file_dir
    db.commit()

    return lesson