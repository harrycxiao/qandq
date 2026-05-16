# qandq

Collection of experiments, utilities, and mini-projects related to:

- Python
- AI workflows
- quantitative modeling
- spreadsheet parsing and structured data extraction
- lightweight CLI tools and automation

This repository contains simplified examples inspired by work completed during my experience at Q&Q AI, an AI startup focused on improving and streamlining financial workflows.

The examples here are intentionally reduced versions designed to demonstrate core ideas and workflows.

---

## Sample Projects

### excel_outline

Parser that converts `.xlsx` workbooks into a structured JSON representation.

Instead of exporting every populated cell individually, the goal is to capture a workbook’s higher-level structure, including:

- key/value relationships
- tables
- contiguous column ranges
- formula patterns and inferred rules

Path:

```text
excel_outline/
```

### excel_cli_agent

Lightweight CLI utility for interacting with Excel workbooks through simple LLM-routed tool selection.

Current supported actions:

- list workbook sheets
- preview the first n rows of a selected sheet

The goal is to explore how spreadsheet data can be exposed through structured tools and used within downstream AI workflows.

Path:

```text
excel_cli_agent/
```
