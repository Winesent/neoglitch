# schemas.py
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional

class ServiceRequestBase(BaseModel):
    client_name: str
    service: str
    date: date
    notes: Optional[str] = None

    @field_validator('date')
    @classmethod
    def date_must_be_in_future(cls, v: date) -> date:
        today = date.today()
        if v <= today:
            raise ValueError('Дата услуги должна быть в будущем (после сегодняшнего дня)')
        return v

class ServiceRequestCreate(ServiceRequestBase):
    pass

class ServiceRequestUpdate(ServiceRequestBase):
    pass

class ServiceRequestOut(ServiceRequestBase):
    id: int

    class Config:
        from_attributes = True