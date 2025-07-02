SHELL := /bin/bash

.PHONY: help setup install clean lint test format run list-workflows
.DEFAULT_GOAL := help
MAKEFLAGS += --silent

help: ## 💬 This help message
	@grep -E '[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 🎭 Initial project setup
	@echo "🎭 Setting up project..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv not found. Please install: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	@make install

install: ## 📦 Install dependencies
	@echo "📦 Installing dependencies..."
	@uv sync --all-groups

clean: ## 🧹 Clean cache and build artifacts
	@echo "🧹 Cleaning up..."
	@uv clean
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

test: ## 🧪 Run tests
	@echo "🧪 Running tests..."
	@uv run pytest

format: ## 🖊️ Format code
	@echo "🖊️ Formatting code..."
	@uv run ruff format

lint: ## � Run linter
	@echo "� Running linter..."
	@uv run pyright

run: ## 🚀 Run workflow (usage: make run <name>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "❌ Usage: make run <workflow_name> [args...]"; \
		echo "💡 Examples:"; \
		echo "   make run financial_analysis 'Microsoft Corporation' MSFT"; \
		echo "   make run calculator"; \
		make list-workflows; \
		exit 1; \
	fi
	@workflow_name="$(word 2,$(MAKECMDGOALS))"; \
	if [ ! -f "src/workflows/$$workflow_name.py" ]; then \
		echo "❌ Workflow '$$workflow_name' not found"; \
		make list-workflows; \
		exit 1; \
	fi; \
	echo "🚀 Running workflow: $$workflow_name"; \
	if [ "$$workflow_name" = "financial_analysis" ]; then \
		args="$(wordlist 3,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))"; \
		if [ -n "$$args" ]; then \
			echo "📊 Company: $$args"; \
			uv run python src/workflows/financial_analysis.py $$args; \
		else \
			echo "💡 Usage: make run financial_analysis 'Company Name' [TICKER]"; \
			echo "💡 Example: make run financial_analysis 'Microsoft Corporation' MSFT"; \
		fi; \
	else \
		uv run python src/workflows/$$workflow_name.py; \
	fi

list-workflows: ## 📋 List available workflows
	@echo "📋 Available workflows:"
	@for file in src/workflows/*.py; do \
		if [ "$$(basename "$$file")" != "__init__.py" ] && [ -f "$$file" ]; then \
			name=$$(basename "$$file" .py); \
			printf "  \033[36m%s\033[0m\n" "$$name"; \
		fi; \
	done

# Allow make run <example_name> without error
%:
	@:
