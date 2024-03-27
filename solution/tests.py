import random
import time
from typing import Self, Callable

import httpx


class Tester:
    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url)
        self.base_url = base_url
        self.accounts = {}

    def ping(self):
        response = self.client.get("/ping")
        assert response.status_code == 200

    def request(self, query: str, behalf: str = None, **kwargs) -> "TestResponse":
        method, path = query.split(" ", maxsplit=1)

        if behalf is not None:
            kwargs["headers"] = {"Authorization": "Bearer " + self.accounts[behalf]}

        start = time.perf_counter()
        response = self.client.request(method, path, **kwargs)
        print(
            f"{method} {path} {response.status_code} {time.perf_counter() - start:.2f}s"
        )
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

    def assertJson(self, data: "dict | json") -> Self:
        assert self.json == data
        print("assertJson OK")
        return self

    def assertLambda(self, func: Callable[["dict | json"], bool]) -> Self:
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


t = Tester("https://edf1-2a00-1fa2-4c4-8596-b09f-b713-4ea1-c1c6.ngrok-free.app/api")
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
    json=register_set("test1", "johnwick1@gmail.com", "123456", "US", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("test1", "johnwick1@gmail.com", "abc1231321321", "US", True),
).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("test1", "johnwick1@gmail.com", "Test123", "ZZ", True),
).assertError(400)

# t.request(
#     "POST /auth/register",
#     json=register_set("**+**-*-*-", "johnwick1@gmail.com", "Test123", "US", True),
# ).assertError(400)

t.request(
    "POST /auth/register",
    json=register_set("1", "johnwick1@gmail.com", "Test123!`", "RU", True),
).assertStatus(201).assertJson(
    {
        "profile": {
            "login": prefix + "1",
            "email": prefix + "johnwick1@gmail.com",
            "countryCode": "RU",
            "isPublic": True,
        },
    }
)

t.request(
    "POST /auth/register",
    json=register_set("2", "johnwick1@gmail.com", "Test123", "RU", True),
).assertError(409)

t.request(
    "POST /auth/register",
    json=register_set("1", "johnwick2@gmail.com", "Test123", "RU", True),
).assertError(409)

t.request(
    "POST /auth/register",
    json=register_set("2", "johnwick1@gmail.com", "Test123!`", "RU", True),
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

# assert (
#     t.request(
#         "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
#     )
#     .assertStatus(200)
#     .json
#     != t.request(
#         "POST /auth/sign-in", json={"login": f"{prefix}1", "password": "Test123!`"}
#     )
#     .assertStatus(200)
#     .json
# )

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

t.request("PATCH /me/profile", "1", json={"isPublic": False}).assertStatus(
    200
).assertJson(
    {
        "login": prefix + "1",
        "email": prefix + f"johnwick1@gmail.com",
        "countryCode": "RU",
        "isPublic": False,
    }
)

phone = f"+{random.randint(1, 999999999)}"

t.request(
    "PATCH /me/profile", "1", json={"isPublic": False, "phone": phone}
).assertStatus(200).assertJson(
    {
        "login": prefix + "1",
        "email": prefix + f"johnwick1@gmail.com",
        "countryCode": "RU",
        "isPublic": False,
        "phone": phone,
    }
)

t.request(
    "PATCH /me/profile", "2", json={"isPublic": True, "phone": phone}
).assertError(409)

t.request("GET /me/profile", "2").assertStatus(200).assertJson(
    {
        "login": prefix + "2",
        "email": prefix + f"johnwick2@gmail.com",
        "countryCode": "BQ",
        "isPublic": False,
    }
)

t.request(f"GET /profiles/{prefix}1", "5").assertError(403)
t.request(f"GET /profiles/{prefix}5", "1").assertError(403)
t.request("POST /friends/add", "1", json={"login": prefix + "5"}).assertStatus(200)
t.request("POST /friends/add", "1", json={"login": prefix + "5"}).assertStatus(200)
t.request("POST /friends/add", "1", json={"login": "unknown"}).assertError(404)
t.request("POST /friends/remove", "1", json={"login": prefix + "5"}).assertStatus(200)
t.request("POST /friends/remove", "1", json={"login": prefix + "5"}).assertStatus(200)
t.request("POST /friends/remove", "1", json={"login": "unknown"}).assertStatus(200)
t.request("GET /friends", "1").assertStatus(200).assertJson([])
t.request("POST /friends/add", "1", json={"login": prefix + "5"}).assertStatus(200)
t.request("GET /friends", "1").assertStatus(200).assertLambda(
    lambda f: len(f) == 1 and f[0]["login"] == prefix + "5" and f[0]["addedAt"]
)

t.request("GET /posts/0000-0000", "1").assertError(404)

post_ids = []

for i in range(105):
    data = (
        t.request(
            "POST /posts/new", "1", json={"content": f"Post {i}", "tags": ["kek"]}
        )
        .assertStatus(200)
        .assertLambda(
            lambda p: p["content"] == f"Post {i}"
            and p["tags"] == ["kek"]
            and p["author"] == prefix + "1"
            and p["id"]
            and p["likesCount"] == 0
        )
        .json
    )
    t.request(f"GET /posts/{data['id']}", "1").assertStatus(200).assertJson(data)
    post_ids.append(data["id"])

    if i % 10 == 0:
        t.request(f"GET /posts/{data['id']}", ["2", "3", "4"][i % 3]).assertError(404)
        time.sleep(0.5)

t.request(f"GET /posts/{post_ids[0]}").assertError(401)

offset = 0
t.request("GET /posts/feed/my?limit=55", "1").assertError(400)
resp = [1]
while resp:
    resp = (
        t.request(f"GET /posts/feed/my?limit=10&offset={offset}", "1")
        .assertStatus(200)
        .json
    )
    offset += len(resp)
    for post in resp:
        assert post["id"] in post_ids
    print(f"Feed offset {offset}")
    time.sleep(0.5)

assert offset == 105

t.request("POST /posts/0000-0000/like", "1").assertError(404)
t.request(f"POST /posts/{post_ids[0]}/like", "1").assertStatus(200)
t.request(f"POST /posts/{post_ids[0]}/like", "1").assertStatus(200)
t.request(f"POST /posts/{post_ids[0]}/like", "1").assertStatus(200)
t.request(f"GET /posts/{post_ids[0]}", "1").assertStatus(200).assertLambda(
    lambda p: p["likesCount"] == 1
)
t.request(f"POST /posts/{post_ids[0]}/dislike", "1").assertStatus(200)
t.request(f"GET /posts/{post_ids[0]}", "1").assertStatus(200).assertLambda(
    lambda p: p["likesCount"] == 0 and p["dislikesCount"] == 1
)
t.request(f"POST /posts/{post_ids[0]}/dislike", "2").assertError(404)
t.request(f"POST /posts/{post_ids[0]}/dislike", "5").assertStatus(200)
t.request(f"GET /posts/{post_ids[0]}", "1").assertStatus(200).assertLambda(
    lambda p: p["likesCount"] == 0 and p["dislikesCount"] == 2
)

# Tests for feed
t.request(f"GET /posts/feed/{prefix}1?limit=55", "1").assertError(400)
t.request(f"GET /posts/feed/{prefix}1", "1").assertStatus(200).assertLambda(
    lambda p: len(p) == 5
)
t.request(f"GET /posts/feed/{prefix}7", "1").assertError(404)
# add to friends
t.request("POST /friends/add", "7", json={"login": prefix + "1"}).assertStatus(200)
t.request(f"GET /posts/feed/{prefix}7", "1").assertStatus(200).assertLambda(
    lambda p: len(p) == 0
)

t.request(f"GET /posts/feed/{prefix}1", "7").assertError(404)
t.request(f"GET /posts/feed/{prefix}1", "5").assertStatus(200).assertLambda(
    lambda p: len(p) == 5
)
