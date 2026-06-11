from fastapi import FastAPI

app = FastAPI(title="World Cup Goal Alert API")

@app.get("/health")
def health_check():
     return {"status": "ok"}
