from pydantic import BaseModel, Field
from typing import List
import re



class CreateUser(BaseModel):
    surname: str = Field(example='Иванов')
    name: str = Field(example='Иван')
    email: str = Field(example='example@mail.com', max_length=64, pattern=re.compile(r'[^@]+@[^@]+\.[^@]+'))
    password: str = Field(example='examplepass', max_length=32, pattern=re.compile(r'^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$'))
    role_id: int = Field(example=1, gt=0)


class UpdateUser(BaseModel):
    surname: str = Field(example='Иванов')
    name: str = Field(example='Иван')
    password: str = Field(example='examplepass', max_length=32, pattern=re.compile(r'^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$'))


class UserLogin(BaseModel):
    email: str = Field(example='example@mail.com', max_length=64, pattern=re.compile(r'[^@]+@[^@]+\.[^@]+'))
    password: str = Field(example='examplepass', max_length=32, pattern=re.compile(r'^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$'))


class CreateRole(BaseModel):
    name: str = Field(example='Студент', min_length=1, max_length=32)


class CreateCourse(BaseModel):
    name: str = Field(example='Программирование')
    desc: str | None = Field(example='')
    price: float = Field(example=5000.0)
    category_id: int = Field(example=1)
    level_id: int = Field(example=1)


class CreateCategory(BaseModel):
    name: str = Field(example='ИТ', min_length=1, max_length=32)


class CreateLevel(BaseModel):
    name: str = Field(example='Легко', min_length=1, max_length=32)


class CreateLesson(BaseModel):
    course_id: int = Field(example=1)
    name: str = Field(example='Программирование 1')
    duration: float = Field(example=40.0)
    order: int = Field(example=1)


class CreateCompletedLesson(BaseModel):
    lesson_id: int = Field(example=1)
    user_id: int = Field(example=1)


class CreateCourseRecord(BaseModel):
    user_id: int = Field(example=1)
    course_id: int = Field(example=1)


class CreateCourseRecordAdmin(BaseModel):
    user_id: int = Field(example=1)
    course_id: int = Field(example=1)
    price: float = Field(example=5000.0, ge=0)