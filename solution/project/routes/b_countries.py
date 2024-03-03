from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from ..database.countries import Country
from ..errors import assert400, assert404
from ..misc import app, get_db


@app.get("/api/countries")
def get_countries(
    region: Annotated[list[str] | None, Query()] = None,
    db: Session = Depends(get_db),
):
    countries = db.query(Country)

    if region:
        allowed_regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
        assert400(all(r in allowed_regions for r in region), "invalid region")
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
    assert404(country is not None)

    return {
        "name": country.name,
        "alpha2": country.alpha2,
        "alpha3": country.alpha3,
        "region": country.region,
    }
