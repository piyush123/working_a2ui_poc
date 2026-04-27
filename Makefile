# Makefile for ADK Agent

.PHONY: install playground test eval eval-all lint deploy

install:
	agents-cli install

playground:
	agents-cli playground

test:
	uv run pytest tests/

eval:
	agents-cli eval run --evalset core_capabilities

eval-all:
	agents-cli eval run --all

lint:
	agents-cli lint

deploy:
	uv run agents-cli deploy --no-confirm-project

register:
	uv run python scripts/register_existing.py

list-agents:
	uv run python scripts/list_gemini_agents.py

delete-agent:
	uv run python scripts/delete_gemini_agent.py
