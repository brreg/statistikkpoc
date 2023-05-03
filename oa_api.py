from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from analyse import analyse
from fastapi.middleware.cors import CORSMiddleware
from google.appengine.api import mail


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
#    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class Form(BaseModel):
    orgnr: str
    year: int
    period: int
    debit_amount: float
    credit_amount: float
    turnover: float


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/orgnr/{orgnr}")
def read_item(
    orgnr: int = 8888888,
    from_and_included_date: Union[str, None] = None,
    to_date: Union[str, None] = None,
    from_and_included_account_id: Union[int, None] = None,
    to_account_id: Union[int, None] = None
    ):
    return analyse(
        str(from_and_included_date),
        str(to_date),
        from_and_included_account_id,
        to_account_id,
    )

@app.post("/orid/{orid}")
def create_form(orid: str, data: Form):
    mail.SendMailToAdmins(
        sender="OA API <dontknow@example.com>",
        subject="New form received",
        body=f"New form received from {orid} with data {data}",
    )
    return {"orid": orid, "data": data}
