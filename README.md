# Multi-Agent Scaffolding

A lightweight framework for orchestrating multi-agent workflows for financial analysis and market intelligence, using Azure AI Agents and Semantic Kernel.

## 🚀 Quick Start

This project is designed to be used in a [VS Code Dev Container](https://code.visualstudio.com/docs/devcontainers/containers). All dependencies are pre-installed for you.


### 1. Open in Dev Container

**Requirements:**
- [Docker](https://www.docker.com/) must be installed and running.
- Use either macOS or Windows with [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/) enabled.
- _Not tested on barebone Windows without WSL._

**Steps:**
1. Clone this repository.
2. Open the folder in VS Code.
3. When prompted, "Reopen in Container" to launch the dev environment.


### 2. Configure Environment Variables

1. Copy `.env.template` to `.env` in the project root:
   ```sh
   cp .env.template .env
   ```
2. Edit `.env` and provide values for all required variables (Azure/OpenAI/Bing credentials, deployment names, etc).

## 🛠️ Usage

### Run a Financial Analysis Workflow

Use the Makefile to run the main workflow:

```
make run financial_analysis Tesco
```

This will:
- Launch the multi-agent orchestration for Tesco 2025 financial analysis
- Save the final report to `outputs/<timestamp>/financial_analysis_report.md`

## 📁 Project Structure

- `src/agents/` — Agent definitions (YAML)
- `src/tools/` — Custom tools for agents
- `src/workflows/` — Workflow orchestration scripts
- `data/` — Example input files (PDFs, Excel)
- `outputs/` — Generated reports

## 📝 License

MIT License. See [LICENSE](LICENSE).