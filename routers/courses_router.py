from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler
from log import Logger



router = APIRouter(prefix='/api/courses', tags=['Courses'])
auth_handler = AuthHandler()
logger = Logger()

models_entity = models.Course
pyd_base = pyd.CourseSchema
pyd_create = pyd.CreateCourse

message_404 = 'Курс не найден'
message_404_many = 'Курсы не найдены'
message_already_exists = 'Курс уже существует'
def delete_message(name):
    return f'Курс \'{name}\' удален'

def auth(jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    
    return {'id': user_db.id, 'role_id': user_db.role_id}
    
def discount(courses, jwt, db):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    course_records = db.query(models.CourseRecord).filter(models.CourseRecord.user_id == user_db.id).count()

    for course in courses:
        if course_records == 1:
            course.price -= course.price * 0.1
        if course_records == 2:
            course.price -= course.price * 0.2
        if course_records >= 3:
            course.price -= course.price * 0.3
    
    return courses


@router.get('/', response_model=List[pyd_base])
def get_courses(page: int | None = Query(default=None, gt=0), 
                limit: int | None = Query(default=None, gt=0), 
                category: str | None = Query(default=None, max_length=32), 
                level: str | None = Query(default=None, max_length=32), 
                db: Session=Depends(get_db)):
    
    courses = db.query(models_entity).all()
    courses_response = courses.copy()
    if not courses:
        raise HTTPException(404, message_404_many)    

    if category:
        category_db = db.query(models.Category).filter(models.Category.name == category).first()
        if not category_db:
            courses = []
            courses_response = []

        for course in courses:
            if course.category_id != category_db.id:
                courses_response.remove(course)
                courses = courses_response.copy()
    if level:
        level_db = db.query(models.Level).filter(models.Level.name.like(level)).first()
        if not level_db:
            courses = []
            courses_response = []

        for course in courses:
            if course.level_id != level_db.id:
                courses_response.remove(course)
    
    if not limit:
        return courses_response
    if not page:
        page = 1

    return courses_response[limit * (page - 1):(limit * page)]
    

@router.get('/{entity_id}', response_model=pyd_base)
def get_entity(entity_id: int, db: Session=Depends(get_db)):
    entity = db.query(models_entity).filter(models_entity.id == entity_id).first()

    if not entity:
        raise HTTPException(404, message_404)

    return entity


@router.get('/auth/', response_model=List[pyd_base])
def get_courses_auth(page: int | None = Query(default=None, gt=0), 
                limit: int | None = Query(default=None, gt=0), 
                category: str | None = Query(default=None, max_length=32), 
                level: str | None = Query(default=None, max_length=32), 
                db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    
    courses = db.query(models_entity).all()
    courses_response = courses.copy()
    if not courses:
        raise HTTPException(404, message_404_many)    

    if category:
        category_db = db.query(models.Category).filter(models.Category.name == category).first()
        if not category_db:
            courses = []
            courses_response = []

        for course in courses:
            if course.category_id != category_db.id:
                courses_response.remove(course)
                courses = courses_response.copy()
    if level:
        level_db = db.query(models.Level).filter(models.Level.name.like(level)).first()
        if not level_db:
            courses = []
            courses_response = []

        for course in courses:
            if course.level_id != level_db.id:
                courses_response.remove(course)
    
    courses_response = discount(courses_response, jwt, db)

    if not limit:
        return courses_response
    if not page:
        page = 1

    return courses_response[limit * (page - 1):(limit * page)]
    

@router.get('/auth/{entity_id}', response_model=pyd_base)
def get_entity_auth(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    entity = db.query(models_entity).filter(models_entity.id == entity_id).first()

    if not entity:
        raise HTTPException(404, message_404)
    entity = discount([entity], jwt, db)
    return entity[0]


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)
    if user_data['role_id'] == 1:
        raise HTTPException(403, 'Доступ запрещен')

    if db.query(models_entity).filter(models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)
    if not db.query(models.Category).filter(models.Category.id == entity.category_id).first():
        raise HTTPException(404, 'Категория не существует')
    if not db.query(models.Level).filter(models.Level.id == entity.level_id).first():
        raise HTTPException(404, 'Сложность не существует')

    entity_db = models_entity()
    entity_db.name = entity.name
    entity_db.desc = entity.desc
    entity_db.price = entity.price
    entity_db.user_id = user_data['id']
    entity_db.category_id = entity.category_id
    entity_db.level_id = entity.level_id

    db.add(entity_db)
    db.commit()

    logger.add('INSERT', entity_db.__tablename__, entity_db)
    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id, models_entity.user_id == user_data['id']).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    if db.query(models_entity).filter(models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)
    if not db.query(models.Category).filter(models.Category.id == entity.category_id).first():
        raise HTTPException(404, 'Категория не существует')
    if not db.query(models.Level).filter(models.Level.id == entity.level_id).first():
        raise HTTPException(404, 'Сложность не существует')
    
    entity_db.name = entity.name
    entity_db.desc = entity.desc
    entity_db.price = entity.price
    entity_db.category_id = entity.category_id
    entity_db.level_id = entity.level_id

    db.commit()

    logger.add('UPDATE', entity_db.__tablename__, entity_db)
    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_data = auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    if user_data['role_id'] != 3:
        if entity_db.user_id != user_data['id']:
            raise HTTPException(403, 'Доступ запрещен')

    db.delete(entity_db)
    db.commit()

    logger.add('DELETE', entity_db.__tablename__, entity_db)
    return {'message': delete_message(entity_db.name)}