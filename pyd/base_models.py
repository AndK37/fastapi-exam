from pydantic import BaseModel, Field



class BaseUser(BaseModel):
    id: int = Field(example=1)
    surname: str = Field(example='Иванов')
    name: str = Field(example='Иван')


class BaseRole(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example='Студент')


class BaseCourse(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example='Программирование')
    desc: str | None = Field(example='')
    price: float = Field(example=5000.0)


class BaseCategory(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example='ИТ')


class BaseLevel(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example='Легко')


class BaseLesson(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example='Программирование 1')
    video_url: str = Field(example='./videos/prog1.mp4')
    duration: float = Field(example=40.0)
    order: int = Field(example=1)