from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

#212342314

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    surname = Column(String(32), nullable=False)
    name = Column(String(32), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))

    role = relationship('Role', backref=backref('users', cascade='all,delete'))

    def __str__(self):
        return f'id: {self.id} surname: {self.surname} name: {self.name} role_id: {self.role_id}'


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)

    def __str__(self):
        return f'id: {self.id} name: {self.name}'


class CourseRecord(Base):
    __tablename__ = 'courses_records'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    record_date = Column(DateTime(timezone=True), server_default=func.now())
    progression = Column(Float, nullable=True, default=0.0)
    price = Column(Float, nullable=True, default=0.0)

    user = relationship('User', backref=backref('courses_records', cascade='all,delete'))
    course = relationship('Course', backref=backref('courses_records', cascade='all,delete'))

    def __str__(self):
        return f'id: {self.id} user_id: {self.user_id} course_id: {self.course_id} record_date: {self.record_date} progression: {self.progression}'


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(64), nullable=False)
    desc = Column(String(1024), nullable=True, default=None)
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    level_id = Column(Integer, ForeignKey('levels.id'), nullable=False)

    user = relationship('User', backref=backref('courses', cascade='all,delete'))
    category = relationship('Category', backref=backref('courses', cascade='all,delete'))
    level = relationship('Level', backref=backref('courses', cascade='all,delete'))

    def __str__(self):
        return f'id: {self.id} name: {self.name} desc: {self.desc} price: {self.price} user_id: {self.user_id} category_id: {self.category_id} level_id: {self.level_id}'


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)

    def __str__(self):
        return f'id: {self.id} name: {self.name}'


class Level(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)

    def __str__(self):
        return f'id: {self.id} name: {self.name}'


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    name = Column(String(32), nullable=False)
    video_url = Column(String(256), nullable=True, default='')
    duration = Column(Float, nullable=False)
    order = Column(Integer, nullable=False)

    course = relationship('Course', backref=backref('lessons', cascade='all,delete'))

    def __str__(self):
        return f'id: {self.id} course_id: {self.course_id} name: {self.name} video_url: {self.video_url} duration: {self.duration} order: {self.order}'


class CompletedLesson(Base):
    __tablename__ = 'comleted_lessons'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    lesson = relationship('Lesson', backref=backref('completed_lessons', cascade='all,delete'))
    user = relationship('User', backref=backref('completed_lessons', cascade='all,delete'))

    def __str__(self):
        return f'id: {self.id} lesson_id: {self.lesson_id} user_id: {self.user_id}'