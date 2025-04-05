from mcp.server.fastmcp import FastMCP
import httpx
import subprocess
import time
import os

# Initialize FastMCP server
mcp = FastMCP("Viterbit MCP")

# Launch FastAPI server programmatically using subprocess
FASTAPI_PORT = 8000
FASTAPI_URL = f"http://127.0.0.1:{FASTAPI_PORT}"

def start_fastapi():
    if os.environ.get("FASTAPI_RUNNING") != "1":
        os.environ["FASTAPI_RUNNING"] = "1"
        subprocess.Popen([
            "uvicorn", "main:app", "--port", str(FASTAPI_PORT),
            "--log-level", "critical"  # suppress logs
        ])

        time.sleep(2)  # Give FastAPI a moment to boot

# Start FastAPI server in the background
start_fastapi()

# Define MCP tools
@mcp.tool()
def candidate_summary(days: int = 7) -> dict:
    """Get a summary of candidates from the last N days."""
    res = httpx.get(f"{FASTAPI_URL}/candidate-summary", params={"days": days})
    res.raise_for_status()
    return res.json()

@mcp.tool()
def compare_stage(stage: str, days: int = 30) -> dict:
    """Compare a stage count between two recent N-day periods."""
    res = httpx.get(f"{FASTAPI_URL}/historical-comparison/{stage}", params={"days": days})
    res.raise_for_status()
    return res.json()

@mcp.tool()
def hiring_velocity() -> float:
    """Get hiring velocity from the last 7 days."""
    return candidate_summary(7).get("hiring_velocity", 0)

# Run the MCP server
if __name__ == "__main__":
    mcp.run()
