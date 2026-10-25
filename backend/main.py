
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from backend.database import db, requests
import backend.schemas as schemas
from backend.services import ai
from backend.services.calculate_score import calculate_score
from backend.services.cache import pre_scoring_cache
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    yield
    db.close()

app = FastAPI(title="Alfa Hackaton API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],        
)

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
    
@app.get("/get_companies_by_client_id/{id}")
def get_companies_by_client_id(id:int):
    companies = requests.get_companies_by_client_id(id)
    if companies == []:
        raise HTTPException(402, "Компании не найдены")
    return companies

@app.get("/get_company_data/{inn}", response_model=schemas.CompanyData)
def get_company_data(inn: str):
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

@app.get("/get_ailog_by_id/{application_id}/{source}", response_model=list[schemas.AILogs])
def get_ailogs(application_id:int, source:str = "user"):
    return requests.get_ailog_by_application_id(application_id, source)

@app.post("/create_application")
def create_application(data: schemas.createApplication):
    result = requests.create_application(**data.model_dump())
    return {"id": result["id"]}

@app.post("/create_pre_scoring")
def create_pre_scoring(application_id: int):
    company_data = requests.get_scoring_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(404, "Данные о компании не были найдены")
    pre_scoring_data = calculate_score(**company_data)
    pre_scoring_cache.set(application_id, pre_scoring_data)
    return pre_scoring_data

@app.post("/create_scoring_result")
def create_scoring_result(application_id: int):
    if pre_scoring_cache.get(application_id) is not None:
        query = requests.create_scoringresult(application_id, **pre_scoring_cache.get(application_id))
        if query is None:
            raise HTTPException(404, "Ошибка в добавлении в scoring_result")
        pre_scoring_cache.delete_cache(application_id)
        return {"id" : query["id"]}
    company_data = requests.get_scoring_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(404, "Данные о компании не были найдены")
    scoring_data = calculate_score(**company_data)
    return requests.create_scoringresult(application_id, **scoring_data)

@app.post("/create_prescoring_ai")
def create_prescoring_ai(application_id: int):
    scoring_result = None
    company_data = None
    if pre_scoring_cache.get(application_id) is not None:
        scoring_result = pre_scoring_cache.get(application_id)
    else:
        scoring_data = requests.get_scoring_data_by_application_id(application_id)
        if scoring_data is None:
            raise HTTPException(403, "Не удалось получить данные скоринга")
        scoring_result = calculate_score(**scoring_data)
    company_data = requests.get_company_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(403, "Не удалось получить данные о компании")
    ai_result = ai.ai_pre_scoring(scoring_result, company_data)
    result = requests.create_ailog(application_id, "user", **ai_result)
    return {"id": result["id"], "ai_answer_text" : ai_result["ai_answer_text"]}

@app.post("/create_manager_summary_ai")
def create_manager_summary_ai(application_id: int):
    scoring_result = None
    company_data = None
    scoring_result = requests.get_scoring_result_by_application_id(application_id)
    if scoring_result is None:
        raise HTTPException(403, "Не удалось получить данные скоринга")
    company_data = requests.get_company_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(403, "Не удалось получить данные о компании")
    ai_result = ai.ai_manager_summary(scoring_result, company_data)
    result = requests.create_ailog(application_id, "manager", **ai_result)
    return {"id": result["id"], "ai_answer_text" : ai_result["ai_answer_text"]}

@app.post("/create_client_result_ai")
def create_client_result_ai(application_id: int):
    scoring_result = None
    company_data = None
    scoring_result = requests.get_scoring_result_by_application_id(application_id)
    if scoring_result is None:
        raise HTTPException(403, "Не удалось получить данные скоринга")
    company_data = requests.get_company_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(403, "Не удалось получить данные о компании")
    manager_comment = requests.get_application_by_id(application_id)["manager_comment"]
    if manager_comment is None:
        ai_result = ai.ai_client_result(scoring_result, company_data)    
    else:
        ai_result = ai.ai_client_result(scoring_result, company_data,manager_comment)   
    result = requests.create_ailog(application_id, "user", **ai_result)
    return {"id": result["id"], "ai_answer_text" : ai_result["ai_answer_text"]}


@app.patch("/update_application/{id}")
def update_application(id: int, data: schemas.updateApplication):
    fields = data.model_dump(exclude_unset=True)  
    if not fields:
        raise HTTPException(400, "Нечего обновлять")
    requests.update_application(id, **fields)

@app.patch("/update_scoringresult/{application_id}")
def update_scoringresult(application_id: int):
    if pre_scoring_cache.get(application_id) is not None:
        query = requests.update_scoringresult_by_application_id(application_id, **pre_scoring_cache.get(application_id))
        if query is None:
            raise HTTPException(404, "Ошибка в добавлении в scoring_result")
        pre_scoring_cache.delete_cache(application_id)
        return {"id" : query["id"]}
    company_data = requests.get_scoring_data_by_application_id(application_id)
    if company_data is None:
        raise HTTPException(404, "Данные о компании не были найдены")
    scoring_data = calculate_score(**company_data)
    result = requests.update_scoringresult_by_application_id(application_id, **scoring_data)
    if result is None:
        raise HTTPException(404, "Скоринг не найден для этой заявки")
    return result

@app.delete("/delete_application/{application_id}")
def delete_application(application_id: int):
    requests.delete_application(application_id)

@app.delete("/delete_scoringresult/{application_id}")
def delete_scoringresult(application_id: int):
    requests.delete_scoringresult(application_id)