from fastapi import FastAPI

app = FastAPI(title="Orbital Copilot Usage API")


@app.get("/health")
def health():
    return {"status": "ok"}
