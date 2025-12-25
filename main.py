from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from datetime import date as date_type
from typing import List
import json

from database import get_db, engine
from models import ServiceRequest, Base
from schemas import ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestOut

app = FastAPI(title="Neoglitch API", description="Импланты будущего — административный API")


# Создание таблиц
@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Для отдачи UI
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# === БЭКЕНД API (основная часть лабораторной) ===

@app.get("/api/requests", response_model=List[ServiceRequestOut])
async def get_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceRequest))
    return result.scalars().all()


@app.post("/api/requests", response_model=ServiceRequestOut, status_code=201)
async def create_request(request: ServiceRequestCreate, db: AsyncSession = Depends(get_db)):
    # Опциональная проверка: услуга должна быть из предопределённого списка
    available_services = [
        "Нейроинтерфейс CortexLink",
        "Ретина-имплант VisionX",
        "Сердечный регулятор CardiCore",
        "Мышечный усилитель MyoBoost",
        "Когнитивный чип NeuroChip",
        "Аудио-имплант SonicEar",
        "Эпидермальный сканер SkinScan",
    ]
    if request.service not in available_services:
        raise HTTPException(status_code=400, detail="Недопустимая услуга")

    db_req = ServiceRequest(**request.model_dump())
    db.add(db_req)
    await db.commit()
    await db.refresh(db_req)
    return db_req


@app.put("/api/requests/{req_id}", response_model=ServiceRequestOut)
async def update_request(
        req_id: int,
        request: ServiceRequestUpdate,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.id == req_id))
    db_req = result.scalar_one_or_none()
    if not db_req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    # Проверка услуги
    available_services = [
        "Нейроинтерфейс CortexLink",
        "Ретина-имплант VisionX",
        "Сердечный регулятор CardiCore",
        "Мышечный усилитель MyoBoost",
        "Когнитивный чип NeuroChip",
        "Аудио-имплант SonicEar",
        "Эпидермальный сканер SkinScan",
    ]
    if request.service not in available_services:
        raise HTTPException(status_code=400, detail="Недопустимая услуга")

    for key, value in request.model_dump().items():
        setattr(db_req, key, value)

    await db.commit()
    await db.refresh(db_req)
    return db_req


@app.delete("/api/requests/{req_id}", status_code=204)
async def delete_request(req_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.id == req_id))
    db_req = result.scalar_one_or_none()
    if not db_req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    await db.execute(delete(ServiceRequest).where(ServiceRequest.id == req_id))
    await db.commit()
    return


# === ФРОНТЕНД (только для удобства, не влияет на оценку бэкенда) ===

@app.get("/", response_class=HTMLResponse)
async def ui_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})