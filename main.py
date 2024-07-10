from fastapi import FastAPI

import models
from database import engine
from router.auth import router
from router.todos import todo_router

from starlette.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static",  StaticFiles(directory='static'), name='static')

models.Base.metadata.create_all(bind=engine)

app.include_router(router)
app.include_router(todo_router)
