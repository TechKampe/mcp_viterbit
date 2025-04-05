# Viterbit MCP Server

This project connects the Viterbit ATS to Claude via the Model Context Protocol (MCP). It exposes candidate metrics and funnel insights using a local FastAPI server and a single-file MCP interface.

## 🔧 Features

- 🚀 FastAPI endpoints for candidate analytics:
  - `/candidate-summary`
  - `/historical-comparison/{stage}`
- 🧠 MCP tools available in Claude:
  - `candidate_summary`
  - `compare_stage`
  - `hiring_velocity`
- 📦 Single entrypoint for Claude (`viterbit_mcp.py`) — boots FastAPI automatically

## 📁 Folder Structure

```
mcp_viterbit/
├── .env
├── .gitignore
├── main.py              # FastAPI server
├── viterbit.py          # Viterbit API integration
├── viterbit_mcp.py      # MCP + FastAPI launcher
├── pyproject.toml       # Managed with uv
├── uv.lock              # Locked deps
├── requirements.txt     # Optional fallback for pip users
```

## 🛠 Requirements

- Python >= 3.10
- [`uv`](https://github.com/astral-sh/uv) for dependency management
- Claude for Desktop (with MCP support)

## ⚙️ Setup Instructions

```bash
# Clone the project
git clone https://github.com/YOUR_USERNAME/mcp-viterbit.git
cd mcp-viterbit

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install uv and dependencies
pip install uv
uv pip install "mcp[cli]" fastapi httpx uvicorn python-dotenv requests python-dateutil

# (Optional) Save dependencies for pip users
uv pip freeze > requirements.txt
```

## ▶️ Run Manually

To run everything locally:

```bash
uv run viterbit_mcp.py
```

## 🧠 Claude Integration

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "viterbit_mcp": {
      "command": "/absolute/path/to/.venv/bin/uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp_viterbit",
        "run",
        "viterbit_mcp.py"
      ],
      "name": "Viterbit MCP",
      "description": "Live insights from your hiring funnel.",
      "message": {
        "role": "system",
        "content": "You are connected to the Viterbit MCP Server. You can call tools to get candidate summaries, hiring velocity, and stage comparisons."
      }
    }
  }
}
```

Restart Claude. You should see the 🛠 hammer icon. Try prompts like:

- "Show me the candidate summary from last week."
- "Compare the Pre-Kämpe stage between this month and last."
- "What's the hiring velocity right now?"

---

Built with ❤️ by Kämpe