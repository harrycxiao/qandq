# LLM Pipeline Prototype

A prototype demonstrating how structured workbook JSON data can be stored in PostgreSQL, exposed through API endpoints, and accessed through an LLM-powered agent workflow.

## Architecture

JSON Workbook Files
↓
PostgreSQL (JSONB)
↓
query.py
↓
FastAPI endpoints
↓
PydanticAI Agent
↓
CLI interaction

## Features

- Stores workbook JSON structures into PostgreSQL JSONB
- Exposes API endpoints for reading/updating records
- Recomputes outputs from dependency rules
- Supports natural language interaction through an LLM agent

## Example

Ask:

Update a and b to 20 and 30

Agent:

Updated values and recomputed outputs...
