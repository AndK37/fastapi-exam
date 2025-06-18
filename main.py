from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import *



app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:5173",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(categories_router)
app.include_router(courses_router)
app.include_router(difficulties_router)
app.include_router(lessons_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(completed_lessons_router)
app.include_router(courses_lessons_router)
app.include_router(courses_records_router)