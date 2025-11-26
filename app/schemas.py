from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int
    current_load: int
    
    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    
    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    external_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OperatorSourceWeightBase(BaseModel):
    operator_id: int
    source_id: int
    weight: int = 1

class OperatorSourceWeightCreate(OperatorSourceWeightBase):
    pass

class OperatorSourceWeight(OperatorSourceWeightBase):
    id: int
    
    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    lead_external_id: Optional[str] = None
    lead_email: Optional[str] = None
    lead_phone: Optional[str] = None
    source_id: int
    message: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    lead_id: int
    operator_id: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DistributionConfig(BaseModel):
    source_id: int
    operators: List[OperatorSourceWeightCreate]