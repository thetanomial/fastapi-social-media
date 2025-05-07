from fastapi import FastAPI, Depends, Path
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

import models 
from models import Posts
from database import engine, SessionLocal 
from starlette import status

from pydantic import BaseModel,Field
from routers import auth,posts


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(
    auth.router
)

app.include_router(
    posts.router
)
