from fastapi import FastAPI
from db import create_db_and_tables

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
