from typing import Union

from fastapi import FastAPI
from analyse import analyse

app = FastAPI()


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

