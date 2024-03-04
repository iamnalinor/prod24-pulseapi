import random
import time
from typing import Self, Callable

import httpx


class Tester:
    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url)
        self.accounts = {}

    def ping(self):
        response = self.client.get("/ping")
        response.raise_for_status()

    def request(self, query: str, behalf: str = None, **kwargs) -> "TestResponse":
        method, path = query.split(" ", maxsplit=1)

        if behalf is not None:
            kwargs["headers"] = {"Authorization": "Bearer " + self.accounts[behalf]}

        response = self.client.request(method, path, **kwargs)
        return TestResponse(response)


class TestResponse:
    def __init__(self, response: httpx.Response):
        assert response.status_code < 500
        assert response.headers["Content-Type"] == "application/json"

        self.resp = response
        self.json = response.json()

    def assertStatus(self, status: int) -> Self:
        assert self.resp.status_code == status
        print("assertStatus OK")
        return self

    def assertJson(self, data: dict) -> Self:
        assert self.json == data
        print("assertJson OK")
        return self

    def assertLambda(self, func: Callable[[dict], bool]) -> Self:
        assert func(self.json)
        print("assertLambda OK")
        return self

    def assertError(self, status: int) -> Self:
        assert self.resp.status_code == status
        assert "reason" in self.json
        assert len(self.json["reason"]) >= 5
        print("assertError OK")
        return self

    def __getitem__(self, item):
        return self.json[item]


prefix = str(random.randint(1, 999999)) + "-"


def register_set(
    login: str,
    email: str,
    password: str,
    countryCode: str,
    isPublic: bool,
    phone: str = None,
    image: str = None,
):
    params = locals().copy()
    if phone is None:
        del params["phone"]
    if image is None:
        del params["image"]
    params["login"] = prefix + params["login"]
    params["email"] = prefix + params["email"]
    return params


t = Tester("http://localhost:8080/api")
t.ping()

t.request("GET /countries").assertStatus(200).assertLambda(lambda data: len(data) > 0)
t.request("GET /countries/BQ").assertStatus(200).assertJson(
    {
        "name": "Bonaire, Sint Eustatius and Saba",
        "alpha2": "BQ",
        "alpha3": "BES",
        "region": "Americas",
    }
)
t.request("GET /countries/XX").assertError(404)


t.request(
    "POST /auth/register",
    json=register_set("test1", "johnwick@gmail.com", "123456", "US", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("test1", "johnwick@gmail.com", "abc1231321321", "US", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("test1", "johnwick@gmail.com", "Test123", "ZZ", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("**+**-*-*-", "johnwick@gmail.com", "Test123", "US", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("1", "johnwick@gmail.com", "Test123!`", "RU", True),
).assertStatus(201).assertJson(
    {
        "profile": {
            "login": prefix + "1",
            "email": prefix + "johnwick@gmail.com",
            "countryCode": "RU",
            "isPublic": True,
        },
    }
)

t.request(
    "POST /auth/register",
    json=register_set("2", "johnwick@gmail.com", "Test123", "RU", True),
).assertError(409)

t.request(
    "POST /auth/register",
    json=register_set("1", "johnwick2@gmail.com", "Test123", "RU", True),
).assertError(409)

t.request(
    "POST /auth/register",
    json=register_set("2", "johnwick@gmail.com", "Test123!`", "RU", True),
).assertError(409)

for i in range(2, 11):
    t.request(
        "POST /auth/register",
        json=register_set(str(i), f"johnwick{i}@gmail.com", "Test123!`", "BQ", False),
    ).assertStatus(201).assertJson(
        {
            "profile": {
                "login": prefix + str(i),
                "email": prefix + f"johnwick{i}@gmail.com",
                "countryCode": "BQ",
                "isPublic": False,
            },
        }
    )

print(
    t.request(
        "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
    )
    .assertStatus(200)
    .json
)
print(
    t.request(
        "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
    )
    .assertStatus(200)
    .json
)

assert (
    t.request(
        "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
    )
    .assertStatus(200)
    .json
    != t.request(
        "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
    )
    .assertStatus(200)
    .json
)

for i in range(1, 11):
    token = (
        t.request(
            "POST /auth/sign-in",
            json={"login": prefix + str(i), "password": "Test123!`"},
        )
        .assertStatus(200)
        .assertLambda(lambda data: "token" in data)
        .json["token"]
    )
    t.accounts[str(i)] = token
