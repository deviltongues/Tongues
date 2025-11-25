from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import requests

from src.decision_engine import analyze_chain

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(STATIC_DIR / "index.html")


WATCH_LIST = ["AAPL", "MSFT", "NVDA", "TSLA", "SPY"]


@app.get("/api/monitor")
def api_monitor():

    results = []

    for symbol in WATCH_LIST:

        entry = {
            "symbol": symbol,
            "signals": [],
            "rows": [],
            "base_rate": None,
            "threshold": None,
        }

        try:
            # call worker
            resp = requests.get(
                f"http://127.0.0.1:9001/fetch?symbol={symbol}",
                timeout=10
            )
            worker_json = resp.json()

            if not worker_json.get("success"):
                entry["error"] = "Worker returned failure"
                results.append(entry)
                continue

            data = worker_json.get("data", [])

            analysis = analyze_chain(data)
            entry["signals"] = analysis["signals"]
            entry["rows"] = analysis["rows"]
            entry["base_rate"] = analysis["base_rate"]
            entry["threshold"] = analysis["threshold"]

        except Exception as e:
            entry["error"] = str(e)

        results.append(entry)

    return {"success": True, "symbols": results}
