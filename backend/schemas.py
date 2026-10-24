
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

class LogIn(BaseModel):
    email: EmailStr
    password: str

class ClientOut(BaseModel):
    name : str
    lastname : str
    middlename : str | None = None
    phone_number : str
    email : EmailStr

class CompanyData(BaseModel):
    bki_data: dict
    fns_data: dict
    fetched_at: datetime | None = None


class ApplicationsInformationDesc(BaseModel):
    name : str
    lastname : str
    middlename : str | None = None
    phone_number : str
    email : EmailStr
    inn: str
    type: str
    amount: int
    term_value: int
    term_unit: str
    aim: str
    status: str
    created: datetime
    updated: datetime

class ApplicationInformation(BaseModel):
    client_name: str
    client_lastname: str
    client_middlename: str | None = None
    email: EmailStr
    phone_number: str
    inn: str    
    application_id: int
    type: str
    amount: int 
    term_value: int 
    term_unit: str 
    aim: str 
    status: str 
    created: datetime 
    updated: datetime
    manager_comment: str | None = None
    bki_data: dict
    fns_data: dict
    fetched_at: datetime
    final_score: int | None = None
    risk_category: str | None = None
    factors: dict 
    recommendation: str | None = None

class AILogs(BaseModel):
    application_id: int
    source: str
    prompt: dict
    ai_answer_text: str
    ai_answer_parsed: dict 
    data: datetime

class createApplication(BaseModel):
    client_id: int
    company_id: int
    application_type: str = Field(default="revolving_credit")
    amount: int = Field(ge=0)
    term_value: int = Field(ge=0)
    term_unit: str = Field(default="days")
    aim: str = Field(min_length=1)
    status: str = Field(default="draft")

class createScoringResult(BaseModel):
    application_id: int
    final_score: int = Field(ge=0)
    risk_category: str = Field(default="middle")
    factors: dict
    recommendation: str

class createAILog(BaseModel):
    application_id: int
    source: str = Field(default="user")
    prompt: dict
    ai_answer_text : str
    ai_answer_parsed : dict

class updateApplication(BaseModel):
    status: str | None = None
    amount: int | None = Field(default=None, ge=0)
    term_value: int | None = Field(default=None, ge=0)
    term_unit: str | None = None
    aim: str | None = Field(default=None, min_length=1)
    manager_comment: str | None = None

class updateScoringResults(BaseModel):
    final_score: int | None = Field(ge=0, default=None)
    risk_category : str | None = None
    factors : str | None =  None
    recommendation: str | None = None

class getScoring(BaseModel):
    application_id: int
    term_value: int
    term_unit: str
    amount: int
    fns_data: dict
    bki_data: dict

