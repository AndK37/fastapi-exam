from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    surname = Column(String(32), nullable=False)
    name = Column(String(32), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))

    role = relationship('Role', backref='users')


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)


class CourseRecord(Base):
    __tablename__ = 'courses_records'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    record_date = Column(DateTime(timezone=True), server_default=func.now())
    progression = Column(Float, nullable=True, default=None)

    user = relationship('User', backref='courses_records')
    course = relationship('Course', backref='courses_records')


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(64), nullable=False)
    desc = Column(String(1024), nullable=True, default=None)
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    level_id = Column(Integer, ForeignKey('levels.id'), nullable=False)

    user = relationship('User', backref='courses')
    category = relationship('Category', backref='courses')
    level = relationship('Level', backref='courses')


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)


class Level(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False, unique=True)


class CourseLesson(Base):
    __tablename__ = 'courses_lessons'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)

    course = relationship('Course', backref='courses_lessons')
    lesson = relationship('Lesson', backref='courses_lessons')


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    name = Column(String(32), nullable=False)
    video_url = Column(String(256), nullable=False)
    duration = Column(Float, nullable=False)
    order = Column(Integer, nullable=False)

    course = relationship('Course', backref='lessons')


class CompletedLesson(Base):
    __tablename__ = 'comleted_lessons'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    lesson = relationship('Lesson', backref='comleted_lessons')
    user = relationship('User', backref='comleted_lessons')
