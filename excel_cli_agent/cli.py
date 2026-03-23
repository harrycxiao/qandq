#make sure to send env:OPENAI_API_KEY=your_api_key_here in the terminal before running this code.
from pydantic import BaseModel
from pydantic_ai import Agent
import sys
from openpyxl import load_workbook
from typing import Literal, Optional

def list_sheets(path):
    wb = load_workbook(path, read_only = True)
    ws = wb.sheetnames
    return ws

def preview(path, sheet, n):
    wb = load_workbook(path, read_only = True)
    ws = wb[sheet]
    rows = []
    count = 1
    for row in ws.iter_rows(values_only = True):
        if count > n:
            break
        rows.append(list(row))
        count += 1
    return rows

class Tool(BaseModel):
    tool: Literal["list_sheets", "preview"]
    sheet: Optional[str] = None
    n: Optional[int] = None

agent = Agent(
    model = "openai:gpt-4.1",
    output_type = Tool,
    system_prompt = """
    You are an agent with two tools to choose from
    and you must only pick one of them.

    The two tools are list_sheets, which lists the sheets of
    a workbook and preview, which lists the first n rows
    of a given sheet in the workbook. You are to decide which 
    tool to use given the user input.
    """ 
)

def cli():
    file = sys.argv[1]
    question = sys.argv[2]

    decision = agent.run_sync(question).output

    if decision.tool == "list_sheets":
        result = list_sheets(file)
    elif decision.tool == "preview":
        result = preview(file, decision.sheet, decision.n)    

    print(result)

if __name__ == "__cli__":
    cli()
