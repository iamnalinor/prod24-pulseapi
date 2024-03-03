from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .errors import ClientRequestError

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ClientRequestError)
async def bad_request_exception_handler(request, exc):
    return JSONResponse({"reason": exc.reason}, status_code=exc.status_code)


def get_db():
    # to prevent import cycle
    from .database.conn import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
