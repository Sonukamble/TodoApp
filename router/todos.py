from typing import Annotated

from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Request, Depends, Form
from models import Todos, Users

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from router.auth import get_current_user

todo_router = APIRouter()

templates = Jinja2Templates(directory='template')

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@todo_router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    return templates.TemplateResponse('home.html', {'request': request, 'todos': todos})


@todo_router.get("/add-todo", response_class=HTMLResponse)
async def add_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('add-todo.html', {'request': request})


@todo_router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo_model = Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@todo_router.get("/update-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo})


@todo_router.post("/update-todo/{todo_id}", response_class=HTMLResponse)
async def create_updated_todo(request: Request, todo_id: int, todo_title: str = Form(), todo_description: str = Form(),
                              todo_priority: int = Form(),
                              db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo_data = db.query(Todos).filter(Todos.id == todo_id).first()

    todo_data.title = todo_title
    todo_data.description = todo_description
    todo_data.priority = todo_priority

    db.add(todo_data)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@todo_router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@todo_router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    todo_model.complete = not todo_model.complete

    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
