from typing import Annotated

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy.orm import Session

from .database.conn import SessionLocal
from .database.countries import Country

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.get("/api/countries")
def get_countries(
    region: Annotated[list[str] | None, Query()],
    db: Session = Depends(get_db),
):
    allowed_regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
    if any(r not in allowed_regions for r in region):
        # set 400 status code
        raise HTTPException(
            status_code=400,
            detail="invalid region passed",
        )

    # Select all fields from the countries table filtered by region and return as JSON

    countries = db.query(Country)
    if region:
        countries = countries.filter(Country.region.in_(region))
    countries = countries.all()

    return [
        {
            "name": country.name,
            "alpha2": country.alpha2,
            "alpha3": country.alpha3,
            "region": country.region,
        }
        for country in countries
    ]


@app.get("/api/countries/{alpha2}")
def get_country(alpha2: str, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.alpha2 == alpha2).first()
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")

    return {
        "name": country.name,
        "alpha2": country.alpha2,
        "alpha3": country.alpha3,
        "region": country.region,
    }
