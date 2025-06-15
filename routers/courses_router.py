from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/courses', tags=['Courses'])
auth_handler = AuthHandler()

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
    if user_db.role_id != 3 and user_db.role_id != 2:
        raise HTTPException(403, 'Доступ запрещен')
    
    return user_db.id
    


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


@router.post('/', response_model=pyd_base)
def create_entity(entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_id = auth(jwt, db)

    if db.query(models_entity).filter(models_entity.name == entity.name).first():
        raise HTTPException(400, message_already_exists)

    entity_db = models_entity()
    entity_db.name = entity.name
    entity_db.desc = entity.desc
    entity_db.price = entity.price
    entity_db.user_id = user_id
    entity_db.category_id = entity.category_id
    entity_db.level_id = entity.level_id

    db.add(entity_db)
    db.commit()

    return entity_db


@router.put('/{entity_id}', response_model=pyd_base)
def update_entity(entity_id: int, entity: pyd_create, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_id = auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id, models_entity.user_id == user_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    entity_db.name = entity.name
    entity_db.desc = entity.desc
    entity_db.price = entity.price
    entity_db.category_id = entity.category_id
    entity_db.level_id = entity.level_id

    db.commit()

    return entity_db


@router.delete('/{entity_id}')
def delete_entity(entity_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_id = auth(jwt, db)

    entity_db = db.query(models_entity).filter(models_entity.id == entity_id, models_entity.user_id == user_id).first()
    if not entity_db:
        raise HTTPException(404, message_404)
    
    db.delete(entity_db)
    db.commit()

    return {'message': delete_message(entity_db.name)}