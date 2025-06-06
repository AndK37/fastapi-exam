from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/roles', tags=['Roles'])
auth_handler = AuthHandler()



@router.get('/', response_model=List[pyd.BaseRole])
def get_all_roles(db: Session=Depends(get_db)):
    roles = db.query(models.Role).all()

    if not roles:
        raise HTTPException(404, 'Роли не найдены')

    return roles


@router.get('/{role_id}', response_model=pyd.BaseRole)
def get_role(role_id: int, db: Session=Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()

    if not role:
        raise HTTPException(404, 'Роль не найдена')

    return role


@router.post('/', response_model=pyd.BaseRole)
def create_role(role: pyd.CreateRole, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    if db.query(models.Role).filter(models.Role.name == role.name).first():
        raise HTTPException(400, 'Роль уже существует')

    role_db = models.Role()
    role_db.name = role.name

    db.add(role_db)
    db.commit()

    return role_db


@router.put('/{role_id}', response_model=pyd.BaseRole)
def update_role(role_id: int, role: pyd.CreateRole, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    role_db = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role_db:
        raise HTTPException(404, 'Роль не найдена')
    
    role_db.name = role.name

    db.commit()

    return role_db


@router.delete('/{role_id}')
def delete_role(role_id: int, db: Session=Depends(get_db), jwt=Depends(auth_handler.auth_wrapper)):
    user_db = db.query(models.User).filter(models.User.email == jwt).first()
    if not user_db:
        raise HTTPException(404, 'Пользователь не найден')
    if user_db.role_id != 3:
        raise HTTPException(403, 'Доступ запрещен')

    role_db = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role_db:
        raise HTTPException(404, 'Роль не найдена')
    
    db.delete(role_db)
    db.commit()

    return {'message': f'Роль \'{role_db.name}\' удалена'}