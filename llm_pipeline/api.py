from fastapi import FastAPI
from pydantic import BaseModel

from query import (
    list_records,
    get_record_by_name,
    get_input_values,
    get_output_values,
    update_input_and_recompute,
)


app = FastAPI(title="LLM Pipeline API")


class UpdateRequest(BaseModel):
    key: str
    value: float


@app.get("/")
def root():
    return {
        "message": "LLM Pipeline API running"
    }


@app.get("/records")
def records():
    return list_records()


@app.get("/records/{name}")
def record_by_name(name: str):
    return get_record_by_name(name)


@app.get("/inputs")
def inputs():
    return get_input_values()


@app.get("/outputs")
def outputs():
    return get_output_values()


@app.post("/inputs/update-and-recompute")
def update(request: UpdateRequest):
    return update_input_and_recompute(
        request.key,
        request.value,
    )
