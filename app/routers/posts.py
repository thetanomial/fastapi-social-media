from fastapi import Depends, Path,APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from models import Posts
from database import SessionLocal 
from starlette import status
from .auth import get_current_user

from pydantic import BaseModel,Field


router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

class PostRequest(BaseModel):
    title : str = Field(
        min_length=3,
        
    )
    description : str = Field(
        min_length=3,
        max_length=100
    )
    priority : int = Field(
        gt = 0,
        lt = 6
    )
    is_published : bool


db_dependency = Annotated[
    Session,
    Depends(get_db)
]

user_dependency = Annotated[dict,Depends(get_current_user)]


@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(
            status_code=401,detail ='Authentication Failed'
        )
    return db.query(Posts).filter(
        Posts.author_id == user.get('id')
    ).all()

@router.get("/post/{post_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db:db_dependency,post_id:int = Path(
    gt = 0
)):
    
    if user is None:
        raise HTTPException(
            status_code=401,detail ='Authentication Failed'
        )
    
    print(user)
    
    post_model = db.query(Posts).filter(
        Posts.id == post_id,
        
    ).filter(Posts.author_id == user.get('id')).first()

    

    if post_model is not None:
        return post_model 
    raise HTTPException(
        status_code = 404,
        detail = 'Post not found'
    )



@router.post("/post",status_code=status.HTTP_201_CREATED)
async def create_post(user:user_dependency,db:db_dependency,post_request:PostRequest):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail = 'Authorization Failed.'
        )
    post_model = Posts(
        **post_request.dict(),
        author_id = user.get('id')
    )
    db.add(post_model)
    db.commit()


@router.put("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(
    user:user_dependency,
    db: db_dependency,
    post_request: PostRequest,
    post_id: int = Path(gt=0)
):
    
    if user is None:
        raise HTTPException(
            status_code=401,detail ='Authentication Failed'
        )


    post_model = db.query(Posts).filter(
        Posts.id == post_id
    )\
    .filter(Posts.author_id == user.get('id')).first()

    if post_model is None:
        raise HTTPException(
            status_code=404,
            detail = "Post not found"
        )
    
    post_model.title = post_request.title
    post_model.description = post_request.description
    post_model.priority = post_request.priority
    post_model.is_published = post_request.is_published

    db.add(post_model)
    db.commit()
    

@router.delete("/post/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(user:user_dependency,db:db_dependency,post_id:int = Path(gt = 0)):
    if user is None:
        raise HTTPException(
            status_code=401,detail ='Authentication Failed'
        )

    post_model = db.query(
        Posts
    ).filter(
        Posts.id == post_id,
        Posts.author_id == user.get('id') 
    ).first()

    print(post_model)

    if post_model is None:
        raise HTTPException(
            status_code=404,
            detail = 'Post not found'
        )

    db.query(Posts).filter(Posts.id == post_id).filter(Posts.author_id == user.get('id')).delete()
    db.commit()