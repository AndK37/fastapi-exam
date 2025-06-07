from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_db
from sqlalchemy.orm import Session
import models
from typing import List
import pyd
from auth import AuthHandler



router = APIRouter(prefix='/api/courses', tags=['Courses'])
auth_handler = AuthHandler()



@router.get('/')
def get_courses(page: int | None = Query(default=None, gt=0), 
                limit: int | None = Query(default=None, ge=0), 
                category: str | None = Query(default=None, max_length=32), 
                level: str | None = Query(default=None, max_length=32), 
                db: Session=Depends(get_db)):
    pass
    

