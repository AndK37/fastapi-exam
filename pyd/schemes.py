from .base_models import *
from typing import List



class UserSchema(BaseUser):
    role: BaseRole


class CourseSchema(BaseCourse):
    user: UserSchema
    category: BaseCategory
    level: BaseLevel


class LessonSchema(BaseLesson):
    course: CourseSchema


class CompletedLessonSchema(BaseCompletedLesson):
    lesson: LessonSchema
    user: UserSchema


class CourseLessonSchema(BaseCourseLesson):
    course: CourseSchema
    lesson: LessonSchema


class CourseRecordSchema(BaseCourseRecord):
    user: UserSchema
    course: CourseSchema


class UserCompletedLessonsSchema(BaseModel):
    user: UserSchema
    completed_lessons: List[LessonSchema]


class CourseAllLessonsSchema(BaseModel):
    course: CourseSchema
    lessons: List[LessonSchema]