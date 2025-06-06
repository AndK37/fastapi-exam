from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/difficulties', tags=['Difficulties'])
auth_handler = AuthHandler()



@router.get('/', response_model=List[pyd.BaseDifficulty])
def get_all_difficulties(db: Session=Depends(get_db)):
    difficulties = db.query(models.Difficulty).all()

    if not difficulties:
        raise HTTPException(404, 'Сложности не найдены')

    return difficulties


@router.get('/{difficulty_id}', response_model=pyd.BaseDifficulty)
def get_difficulty(difficulty_id: int, db: Session=Depends(get_db)):
    difficulty = db.query(models.Difficulty).filter(models.Difficulty.id == difficulty_id).first()

    if not difficulty:
        raise HTTPException(404, 'Сложность не найдена')

    return difficulty


@router.post('/', response_model=pyd.BaseDifficulty)
def create_difficulty(difficulty: pyd.CreateDifficulty, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    if db.query(models.Difficulty).filter(models.Difficulty.name == difficulty.name).first():
        raise HTTPException(400, 'Сложность уже существует')

    difficulty_db = models.Difficulty()
    difficulty_db.name = difficulty.name

    db.add(difficulty_db)
    db.commit()

    return difficulty_db


@router.put('/{difficulty_id}', response_model=pyd.BaseDifficulty)
def update_difficulty(difficulty_id: int, difficulty: pyd.CreateDifficulty, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    difficulty_db = db.query(models.Difficulty).filter(models.Difficulty.id == difficulty_id).first()
    if not difficulty_db:
        raise HTTPException(404, 'Сложность не найдена')
    
    difficulty_db.name = difficulty.name

    db.commit()

    return difficulty_db


@router.delete('/{difficulty_id}')
def delete_difficulty(difficulty_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    difficulty_db = db.query(models.Difficulty).filter(models.Difficulty.id == difficulty_id).first()
    if not difficulty_db:
        raise HTTPException(404, 'Сложность не найдена')
    
    db.delete(difficulty_db)
    db.commit()

    return {'message': f'Сложность \'{difficulty_db.name}\' удалена'}