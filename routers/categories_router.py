from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/categories', tags=['Categories'])
auth_handler = AuthHandler()



@router.get('/', response_model=List[pyd.BaseCategory])
def get_all_categories(db: Session=Depends(get_db)):
    categories = db.query(models.Category).all()

    if not categories:
        raise HTTPException(404, 'Категории не найдены')

    return categories


@router.get('/{category_id}', response_model=pyd.BaseCategory)
def get_category(category_id: int, db: Session=Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not category:
        raise HTTPException(404, 'Категория не найдена')

    return category


@router.post('/', response_model=pyd.BaseCategory)
def create_category(category: pyd.CreateCategory, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    if db.query(models.Category).filter(models.Category.name == category.name).first():
        raise HTTPException(400, 'Категория уже существует')

    category_db = models.Category()
    category_db.name = category.name

    db.add(category_db)
    db.commit()

    return category_db


@router.put('/{category_id}', response_model=pyd.BaseCategory)
def update_category(category_id: int, category: pyd.CreateCategory, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    category_db = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_db:
        raise HTTPException(404, 'Категория не найдена')
    
    category_db.name = category.name

    db.commit()

    return category_db


@router.delete('/{category_id}')
def delete_category(category_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    category_db = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_db:
        raise HTTPException(404, 'Категория не найдена')
    
    db.delete(category_db)
    db.commit()

    return {'message': f'Категория \'{category_db.name}\' удалена'}


