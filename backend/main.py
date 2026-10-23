
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from backend.database import db, requests
import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    yield
    db.close()

app = FastAPI(title="Alfa Hackaton API", lifespan=lifespan)

@app.post("/login", response_model=schemas.ClientOut)
def LogIn(data: schemas.LogIn):
    client = requests.get_client(data.email, data.password)
    if client is None:
        raise HTTPException(403, "Пользователь не найден")
    else:
        return client
    
@app.get("/get_client_by_id/{id}", response_model=schemas.ClientOut)
def get_client_by_id(id: int):
    client = requests.get_client_by_id(id)
    if client is None:
        raise HTTPException(403, "Пользователь не найден")
    else:
        return client

@app.get("/get_company_data/{inn}", response_model=schemas.CompanyData)
def get_company_data(inn: int):
    company = requests.get_company_data(inn)
    if company is None:
        raise HTTPException(403, "Компания не найдена")
    else:
        return company
    
@app.get("/get_applications_analysis", response_model=list[schemas.ApplicationsInformationDesc])
def get_applications_analysis():
    return requests.get_applications_for_analysis()

@app.get("/get_users_applications/{id}", response_model=list[schemas.ApplicationsInformationDesc])
def get_users_applications(id:int):
    return requests.get_users_applications(id)

@app.get("/get_application_by_id/{id}", response_model=schemas.ApplicationInformation)
def get_application_by_id(id:int):
    application = requests.get_application_by_id(id)
    if application is None:
        raise HTTPException(403, "Заявка не найдена")
    else:
        return application

@app.get("/get_ailogs", response_model=list[schemas.AILogs])
def get_ailogs():
    return requests.get_ailogs()

@app.post("/create_application/")
def create_application(data: schemas.createApplication):
    result = requests.create_application(**data.model_dump())
    return {"id": result["id"]}

@app.post("/create_scoringresult")
def create_scoringresult(data: schemas.createScoringResult):
    result = requests.create_scoringresult(**data.model_dump())
    return {"id": result["id"]}

@app.post("/create_ailog")
def create_ailog(data: schemas.createAILog):
    result = requests.create_ailog(**data.model_dump())
    return {"id": result["id"]}

@app.patch("/update_application/{id}")
def update_application(id: int, data: schemas.updateApplication):
    fields = data.model_dump(exclude_unset=True)  
    if not fields:
        raise HTTPException(400, "Нечего обновлять")
    requests.update_application(id, **fields)

@app.patch("/update_scoringresult/{id}")
def update_scoringresult(id: int, data: schemas.updateScoringResults):
    fields = data.model_dump(exclude_unset=True)  
    if not fields:
        raise HTTPException(400, "Нечего обновлять")
    requests.update_scoringresult(id, **fields)


@app.delete("/delete_application/{application_id}")
def delete_application(application_id: int):
    requests.delete_application(application_id)

@app.delete("/delete_scoringresult/{application_id}")
def delete_scoringresult(application_id: int):
    requests.delete_scoringresult(application_id)