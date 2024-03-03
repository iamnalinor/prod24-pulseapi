from ..misc import app


@app.get("/api/ping")
def ping():
    return {"status": "ok"}
