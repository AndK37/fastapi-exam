from sqlalchemy.orm import Session
from database import engine
import models
from datetime import date
import os
from auth import AuthHandler



models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

auth_handler = AuthHandler()



with Session(bind=engine) as session:
    try:
        os.mkdir('lessons')
    except:
        pass

    try:
        file = open('log.txt', 'w+')
    except:
        pass


    role1 = models.Role(name='Студент')
    role2 = models.Role(name='Преподаватель')
    role3 = models.Role(name='Админ')
    roles = [role1, role2, role3]
    session.add_all(roles)

    user1 = models.User(surname='Петров', name='Алексей', email='alexey.petrov@mail.com', password_hash=auth_handler.get_password_hash('QWErty123#'), role_id=1)
    user2 = models.User(surname='Васильева', name='Ольга', email='olga.vasilyeva@yandex.ru', password_hash=auth_handler.get_password_hash('QWErty123#'), role_id=2)
    user3 = models.User(surname='Соколовская', name='Екатерина', email='ekaterina.sokolovskaya@gmail.com', password_hash=auth_handler.get_password_hash('QWErty123#'), role_id=3)
    users = [user1, user2, user3]
    session.add_all(users)

    category1 = models.Category(name='ИТ')
    category2 = models.Category(name='Физика')
    category3 = models.Category(name='Химия')
    categories = [category1, category2, category3]
    session.add_all(categories)

    level1 = models.Level(name='Легко')
    level2 = models.Level(name='Нормально')
    level3 = models.Level(name='Сложно')
    difficulties = [level1, level2, level3]
    session.add_all(difficulties)

    course1 = models.Course(name='Программирование - легко', desc='', price=5000.0, user_id=2, category_id=1, level_id=1)
    lesson11 = models.Lesson(course_id=1, name='Программирование 1', video_url='', duration=40, order=1)
    lesson12 = models.Lesson(course_id=1, name='Программирование 2', video_url='', duration=40, order=2)
    lesson13 = models.Lesson(course_id=1, name='Программирование 3', video_url='', duration=40, order=3)

    course2 = models.Course(name='Физика - средне', desc='', price=10000.0, user_id=2, category_id=2, level_id=2)
    lesson21 = models.Lesson(course_id=2, name='Физика 1', video_url='', duration=40, order=1)
    lesson22 = models.Lesson(course_id=2, name='Физика 2', video_url='', duration=40, order=2)
    lesson23 = models.Lesson(course_id=2, name='Физика 3', video_url='', duration=40, order=3)

    course3 = models.Course(name='Химия - сложно', desc='', price=15000.0, user_id=2, category_id=3, level_id=3)
    lesson31 = models.Lesson(course_id=3, name='Химия 1', video_url='', duration=40, order=1)
    lesson32 = models.Lesson(course_id=3, name='Химия 2', video_url='', duration=40, order=2)
    lesson33 = models.Lesson(course_id=3, name='Химия 3', video_url='', duration=40, order=3)

    courses = [course1, course2, course3]
    lessons = [lesson11, lesson12, lesson13, lesson21, lesson22, lesson23, lesson31, lesson32, lesson33]

    session.add_all(courses)
    session.add_all(lessons)

    course_record1 = models.CourseRecord(user_id=1, course_id=1, progression=0.33, price=5000)
    session.add(course_record1)

    completed_lesson = models.CompletedLesson(lesson_id=1, user_id=1)
    session.add(completed_lesson)

    session.commit()