from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from fastapi import WebSocket


class VerificationCode(BaseModel):
    verification_code: str

class EvidenceBase(BaseModel):
    link: str
    idRequestForEvidence: int
    deliveryDate: date

class EvidenceCreate(EvidenceBase):
    pass

class Evidence(EvidenceBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UpdateRequestForEvidence(BaseModel):
    requiredDocument: str
    description: str
    step_id: int
    user_id: int
    evidenceValidationDate: date
    deliveryDate: date
    is_validated: bool
    is_actived: bool
    id: int

class RequestForEvidenceBase(BaseModel):
    requiredDocument: str
    description: str
    step_id: int
    user_id: int
    evidenceValidationDate: date
    deliveryDate: date
    is_validated: bool
    is_actived: bool

class RequestForEvidenceCreate(RequestForEvidenceBase):
    pass

class RequestForEvidence(RequestForEvidenceBase):
    id: int
    evidences: List[Evidence]

    class Config:
        from_attributes = True


class UpdateStep(BaseModel):
    step_id: int
    name: str
    endDate: date
    endingDate: date
    process_id: int
    objective: str
    priority: str
    order: int
    is_active: bool

class StepBase(BaseModel):
    name: str
    endDate: date
    endingDate: date
    process_id: int
    objective: str
    priority: str
    order: int
    is_active: bool

class StepCreate(StepBase):
    pass

class Step(StepBase):
    id: int
    requests: List[RequestForEvidence]

    class Config:
        from_attributes = True


class ProcessBase(BaseModel):
    title: str
    description:str
    objective: str
    endingDate: date
    createDate: date
    lastUpdate: date
    is_active: bool
    priority: str
    status: str

class ProcessCreate(ProcessBase):
    pass


class ProcessUpdate(ProcessBase):
    id: int
    
    class Config:
        from_attributes = True

class Process(ProcessBase):
    id: int
    steps: List[Step]

    class Config:
        from_attributes = True

class DeleteProcess(BaseModel):
    id: int
    is_active: bool

class DeleteStep(BaseModel):
    id: int
    is_active: bool

class DeleteRequest(BaseModel):
    id: int
    is_active: bool


class UserBase(BaseModel):
    name: str
    email: str
    role: str
    team: str
    is_active: bool

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_2fa_enable: Optional[bool]
    

    class Config:
        from_attributes = True


class ProcessUserBase(BaseModel):
    user_id: int
    process_id: int

class ProcessUserCreate(ProcessUserBase):
    pass

class ProcessUser(ProcessUserBase):
    user: User
    process: Process    
    class Config:
        from_attributes = True

class ProcessUserOnlyUser(ProcessUserBase):
    user: User  
    class Config:
        from_attributes = True



class UserStepBase(BaseModel):
    user_id: int
    step_id: int

class UserStepCreate(UserStepBase):
    pass

class UserStep(UserStepBase):
    step: Step
    user: User
    class Config:
        from_attributes = True

class UserStepOnlyUser(UserStepBase):
    user: User
    class Config:
        from_attributes = True


class StepForProcess(StepBase):
    id: int
    requests: List[RequestForEvidence]
    users: List[UserStepOnlyUser]


    class Config:
        from_attributes = True


class ProcessAll(ProcessBase):
    id: int
    steps: List[StepForProcess]
    users: List[ProcessUserOnlyUser]

    class Config:
        from_attributes = True

class UserGet(UserBase):
    id: int
    processes: List[ProcessUser]
    steps: List[UserStep]

    class Config:
        from_attributes = True


class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None
    team: str | None = None

    class Config:
        from_attributes = True

class WebSocketUser(BaseModel):
    websocket: WebSocket
    user: User

    class Config:
        arbitrary_types_allowed=True