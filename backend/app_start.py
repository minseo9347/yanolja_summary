import uvicorn

# cli 실행 : uvicorn app.main:app --reload

if __name__ == "__main__":
  uvicorn.run('main:app', 
              host='localhost', port=8000, reload=True)