from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime

class UserBase(BaseModel):
    name: str
    email: str
    role: str
    status: str

class UserResponse(UserBase):
    id: str
    lastActive: str # We'll format this nicely in the service
    
    model_config = ConfigDict(from_attributes=True)
