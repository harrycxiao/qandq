from dotenv import load_dotenv
import requests

from pydantic import BaseModel
from pydantic_ai import Agent


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"


class AgentResponse(BaseModel):
    message: str


agent = Agent(
    model="openai:gpt-5.1",
    output_type=AgentResponse,
    system_prompt="""
You are an assistant that interacts with a workbook backend.

You have tools to:
- list records
- read records
- read inputs
- read outputs
- update inputs

Use tools whenever needed.

Important:
- update_input_tool updates only one input key per call.
- If the user asks to update multiple inputs, call update_input_tool separately for each key.
- After updates, call get_outputs_tool to verify the final outputs before answering.
- Never claim an update happened unless the tool returned confirmation.
""",
)


@agent.tool_plain
def list_records_tool():
    response = requests.get(f"{BASE_URL}/records")
    return response.json()


@agent.tool_plain
def get_record_by_name_tool(name: str):
    response = requests.get(f"{BASE_URL}/records/{name}")
    return response.json()


@agent.tool_plain
def get_inputs_tool():
    response = requests.get(f"{BASE_URL}/inputs")
    return response.json()


@agent.tool_plain
def get_outputs_tool():
    response = requests.get(f"{BASE_URL}/outputs")
    return response.json()


@agent.tool_plain
def update_input_tool(key: str, value: float):
    response = requests.post(
        f"{BASE_URL}/inputs/update-and-recompute",
        json={
            "key": key,
            "value": value,
        },
    )

    return response.json()


if __name__ == "__main__":
    while True:
        user_input = input("\nAsk: ")

        if user_input.lower() == "quit":
            break

        result = agent.run_sync(user_input)

        print("\nAgent:")
        print(result.output.message)
