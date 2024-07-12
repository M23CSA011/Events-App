from pydantic import BaseModel, ConfigDict , EmailStr , field_validator
from datetime import datetime
from typing import Optional,List


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    email:EmailStr
    name:str
    created_at:datetime
    role:str

class UserCreate(BaseModel):
    email:EmailStr
    name:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: Optional[int] = None


class Register(BaseModel):
    name:str
    age:int
    gender:str

    @field_validator('age')
    def age_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('Age must be a non-negative integer')
        return value

class RegisterCreate(BaseModel):
    event_id:int
    registrations:List[Register]
    
    @field_validator('event_id')
    def eventid_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('Event id must be a non-negative integer')
        return value

class Event(BaseModel):
    
    title:str
    description:str
    location:str
    price:int
    event_datetime:datetime

    @field_validator('price')
    def price_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('Price must be a non-negative integer')
        return value

    @field_validator('event_datetime')
    def event_datetime_must_be_future(cls, value):
        if value <= datetime.now(value.tzinfo): 
            raise ValueError('Event datetime must be in the future')
        return value
    
class GetEventsUser(Event):
    id:int

class DeleteEvent(BaseModel):
    event_id:int

class GetRegister(Register):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    event_id:int
    user_registered_at:datetime
    user_id:int
    user:UserOut

class GetRegisterEvent(GetRegister):
    model_config = ConfigDict(from_attributes=True)
    event:GetEventsUser

class NumRegister(BaseModel):
    event_id: int
    count: int


class GetEventsAdmin(Event):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    event_created_at:datetime
    owner_id:int
    owner:UserOut

