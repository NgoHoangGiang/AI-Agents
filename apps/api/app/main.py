from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Personal Copilot API is running!"}