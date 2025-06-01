from .base_models import *
from typing import List



class UserSchema(BaseUser):
    role: BaseRole


class CourseSchema(BaseCourse):
    user: UserSchema
    category: BaseCategory
    difficulty: BaseDifficulty


class LessonSchema(BaseLesson):
    course: CourseSchema