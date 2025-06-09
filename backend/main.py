""" 
simple todo
fastAPI를 활용한 DB CRUD
명령 실행 : 
  - uvicorn main:app --reload
  또는
  - python app_start.py
"""
# main.py

from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from schema import ReviewSummaryResponse
from database import engine, sessionlocal
from sqlalchemy.orm import Session
import models

# models에 정의한 모든 클래스, 연결한 DB엔진에 테이블로 생성
models.Base.metadata.create_all(bind=engine)

# FastAPI() 객체 생성
app = FastAPI()

# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")

# static 폴더(정적파일 폴더)를 app에 연결
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = sessionlocal()
    try:
        # yield 키워드는 FastAPI가 함수의 실행을 일시 중지하고 데이터베이스 세션을 호출자에게 반환하도록 지시
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    accmmodation_list = db.query(models.AccommodationInfo.id, models.AccommodationInfo.name).all()
    # accommodation_list = [{"id": item[0], "name": item[1]} for item in accommodation_list]
    acc_list = []
    for acc in accmmodation_list:
        item = {}
        # print(acc.id, acc.name)
        item['id'] = acc.id
        item['name'] = acc.name
        acc_list.append(item)
        print(acc_list)
    
    return  acc_list

@app.get("/review_summary/{id}")
async def review_summary(request: Request, id: int , db: Session = Depends(get_db)):
    # print(id)
    
    # 폼에서 숙소 ID를 가져옴
    review = db.query(models.ReviewSummary).filter(models.ReviewSummary.id == id).order_by(models.ReviewSummary.id.desc()).first()
    # Pydantic 스키마 객체로 변환
    review_response = ReviewSummaryResponse(
            id=review.id,
            accommodation_id=review.accommodation_id,
            summary_good=review.summary_good,
            summary_bad=review.summary_bad,
            date=review.date,
            )
    return review_response