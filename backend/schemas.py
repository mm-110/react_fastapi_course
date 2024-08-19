import datetime as dt
import pydantic as pyd

class UserBase(pyd.BaseModel):
    email: str

class UserCreate(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class LeadBase(pyd.BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str

class LeadCreate(LeadBase):
    pass

    class Config:
        from_attributes = True

class Lead(LeadBase):
    id: int
    owner_id: int
    data_created: dt.datetime
    data_last_update: dt.datetime

    class Config:
        from_attributes = True