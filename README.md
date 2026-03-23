# qandq

Collection of small experiments, utilities, and mini-projects related to:

- Python
- math and statistics
- quantitative modeling
- spreadsheet / parsing tools
- lightweight CLI workflows

This repository is where I build smaller focused projects while exploring new ideas.

---

## Projects

### excel_outline

Parser that converts `.xlsx` workbooks into a compact JSON outline.

Instead of dumping every populated cell, the goal is to describe the workbook's
high-level structure, including:

- key/value maps
- tables
- integer column ranges
- formula-based series rules

Path:

```text
excel_outline/
```

### excel_cli_agent

Small CLI utility for interacting with Excel workbooks through simple
LLM-routed tool selection.

Current supported actions:

- list workbook sheets
- preview the first n rows of a selected sheet

Path:

```text
excel_cli_agent/
```
