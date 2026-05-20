#API endpoitns for Postgres
from fastapi import FastAPI
from pydantic import BaseModel

# import functions from query.py
from query import (
    list_records,
    get_record_by_name,
    get_input_values,
    get_output_values,
    update_input_and_recompute
)


app = FastAPI(
    title="LLM Pipeline API"
)


# -------------------------
# Request model
# -------------------------

class UpdateRequest(BaseModel):
    key: str
    value: float


# -------------------------
# GET endpoints
# -------------------------

@app.get("/")
def root():
    return {
        "message": "LLM Pipeline API running"
    }


@app.get("/records")
def records():
    """
    Return metadata for all records.
    """
    return list_records()


@app.get("/records/{name}")
def record_by_name(name: str):
    """
    Return full JSON record.

    Example:
    /records/Input
    /records/Output
    """
    return get_record_by_name(name)


@app.get("/inputs")
def inputs():
    """
    Return clean input values.
    """
    return get_input_values()


@app.get("/outputs")
def outputs():
    """
    Return clean output values.
    """
    return get_output_values()


# -------------------------
# POST endpoint
# -------------------------

@app.post("/inputs/update-and-recompute")
def update(request: UpdateRequest):
    """
    Update one input and recompute outputs.

    Example request body:

    {
        "key":"a",
        "value":10
    }
    """

    return update_input_and_recompute(
        request.key,
        request.value
    )
