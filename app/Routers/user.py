from fastapi import HTTPException , status , Depends , APIRouter
from sqlalchemy.orm import Session
from .. import models , schemas , utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post('',status_code=status.HTTP_201_CREATED)
def create_users(user:schemas.UserCreate,db:Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email==user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    hashed_passwored = utils.hash(user.password)
    user.password = hashed_passwored
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_pydantic_user = schemas.UserOut(**new_user.__dict__) 

    return new_pydantic_user

@router.get("/{id}")
def get_user(id:int,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {id} was not found")
    
    new_pydantic_user = schemas.UserOut(**user.__dict__)

    return new_pydantic_user 