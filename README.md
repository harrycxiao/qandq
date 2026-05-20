# qandq

Collection of experiments, utilities, and mini-projects related to:

- Python
- AI workflows
- structured data systems
- spreadsheet parsing
- lightweight agent tooling
- financial workflows

This repository contains simplified examples inspired by work completed during my experience at Q&Q AI, an AI startup focused on improving and streamlining financial workflows.

The projects below are arranged roughly in the order they were built and reflect an evolving exploration of how structured data can move through AI systems.

---

## Sample Projects

### excel_cli_agent

Simple CLI utility for interacting with Excel workbooks through LLM-routed tool selection.

Supported actions:

- list workbook sheets
- preview first n rows of a sheet

Architecture:

```text
User Question
↓
LLM tool selection
↓
Python function
↓
Workbook output
```

Goal:

Explore basic tool routing and agent workflows.

Path:

```text
excel_cli_agent/
```

---

### excel_outline

Parser that converts `.xlsx` workbooks into structured JSON representations.

Rather than exporting every populated cell individually, the parser attempts to capture workbook structure:

- key/value relationships
- tables
- contiguous ranges
- inferred rules
- dependencies

Architecture:

```text
Excel Workbook
↓
Parser
↓
Structured JSON
```

Goal:

Represent spreadsheets in a form usable by downstream systems.

Path:

```text
excel_outline/
```

---

### llm_pipeline

Prototype demonstrating how structured workbook data can move through backend systems and become accessible to LLM workflows.

Architecture:

```text
Workbook JSON
↓
PostgreSQL (JSONB)
↓
query.py
↓
FastAPI
↓
PydanticAI tools
↓
CLI interaction
```

Features:

- stores workbook structures in PostgreSQL JSONB
- exposes API endpoints
- updates inputs and recomputes outputs
- enables natural language interaction through LLM-selected tools

Example:

```text
Ask:
update a and b to 20 and 30

Agent:
Updated values and recomputed outputs...
```

Goal:

Explore end-to-end AI workflows connecting structured data, databases, APIs, and LLM agents.

Path:

```text
llm_pipeline/
```
