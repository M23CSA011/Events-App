from fastapi import HTTPException,status,Response,Depends,APIRouter,Query
from sqlalchemy.orm import Session
from .. import models,schemas,oauth2 
from ..database import get_db
from typing import Optional
from sqlalchemy import func,desc

router = APIRouter(
    prefix = "/registrations",
    tags = ["Registrations"]
)

@router.get("/getall/{id}")
def get_all_registrations(id:int,db:Session = Depends(get_db),
    limit: int = Query(10, description="Limit the number of users returned"),
    gender: Optional[str] = Query(None, description="Filter by gender (Male, Female, other)"),
    min_age: Optional[int] = Query(None, description="Filter by minimum age"),
    max_age: Optional[int] = Query(None, description="Filter by maximum age"),
    name: Optional[str] = Query(None, description="Search users by name"),                      
    curr_user:int=Depends(oauth2.get_current_user)):
    
    if curr_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    
    query = db.query(models.Registration).filter(models.Registration.event_id == id)
    
    if name:
        query = query.filter(models.Registration.name.contains(name))

    if gender:
        query = query.filter(models.Registration.gender == gender)

    if min_age is not None:
        query = query.filter(models.Registration.age >= min_age)

    if max_age is not None:
        query = query.filter(models.Registration.age <= max_age)
    
    results = query.limit(limit).all()

    all_events = []
    for event in results:
        event_dict = event.__dict__.copy()
        event_dict['user']=event.user.__dict__.copy()
        event_dict['event']=event.event.__dict__.copy()
        all_events.append(schemas.GetRegisterEvent(**event_dict))

    return all_events

@router.get("/getregistered")
def get_curruser_registrations(db:Session=Depends(get_db),
    limit: int = Query(10, description="Limit the number of users returned"),
    gender: Optional[str] = Query(None, description="Filter by gender (Male, Female, other)"),
    min_age: Optional[int] = Query(None, description="Filter by minimum age"),
    max_age: Optional[int] = Query(None, description="Filter by maximum age"),
    name: Optional[str] = Query(None, description="Search users by name"),
    curr_user:int=Depends(oauth2.get_current_user)):

    query = db.query(models.Registration).filter(models.Registration.user_id==curr_user.id).order_by(desc(models.Registration.user_registered_at))
    
    if name:
        query = query.filter(models.Registration.name.contains(name))

    if gender:
        query = query.filter(models.Registration.gender == gender)

    if min_age is not None:
        query = query.filter(models.Registration.age >= min_age)

    if max_age is not None:
        query = query.filter(models.Registration.age <= max_age)

    results = query.limit(limit).all()
    
    all_events = []
    for event in results:
        event_dict = event.__dict__.copy()
        event_dict['user']=event.user.__dict__.copy()
        event_dict['event']=event.event.__dict__.copy()
        all_events.append(schemas.GetRegisterEvent(**event_dict))

    return all_events

@router.post('',status_code=status.HTTP_201_CREATED)
def register_events(events:schemas.RegisterCreate,db:Session=Depends(get_db),curr_user:int=Depends(oauth2.get_current_user)):

    event = db.query(models.Event).filter(models.Event.id == events.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Event with id {events.event_id} does not exist")

    created_events = []
    
    for event in events.registrations:

        already_registered = db.query(models.Registration).filter(
            models.Registration.event_id == events.event_id,
            models.Registration.user_id == curr_user.id,
            models.Registration.name == event.name,
            models.Registration.age == event.age,
            models.Registration.gender == event.gender
        ).first()

        if already_registered:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already registered for this event with the same details")

        if event.gender not in ["Male", "Female", "other"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender")
    
        new_event = models.Registration(user_id=curr_user.id,event_id=events.event_id,**event.model_dump())
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        new_event_dict = new_event.__dict__.copy()
        new_event_dict['user'] = new_event.user.__dict__.copy()
        new_pydantic_event = schemas.GetRegister(**new_event_dict)
        created_events.append(new_pydantic_event)

    return created_events

@router.get('/NumRegistrations')
def get_Num_Registrations(db:Session=Depends(get_db)):
    event_counts = db.query(
        models.Registration.event_id,
        func.count(models.Registration.event_id).label('count')
    ).group_by(models.Registration.event_id).all()
    
    pydantic_event_counts = []
    for event_id,count in event_counts:
        pydantic_event_counts.append(schemas.NumRegister(event_id=event_id,count=count))
    return pydantic_event_counts

@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(event: schemas.DeleteEvent, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    if curr_user.role == "admin":
        registrations = db.query(models.Registration).filter(models.Registration.event_id == event.event_id).all()
    else:
        registrations = db.query(models.Registration).filter(models.Registration.event_id == event.event_id, models.Registration.user_id == curr_user.id).all()

    if not registrations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registrations not found")

    for registration in registrations:
        db.delete(registration)
    
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)




