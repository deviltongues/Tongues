# src/lseg_client.py
import requests

WORKER_URL = "http://127.0.0.1:9001/fetch"


def get_option_chain(symbol: str):
    """
    Call the LSEG worker (port 9001) to fetch the option chain.
    Returns a list of dicts (one per option row).
    """
    try:
        url = f"{WORKER_URL}?symbol={symbol}"
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("success"):
            return data.get("data", [])
        else:
            print("Worker error:", data)
            return []
    except Exception as e:
        print("Client Exception:", e)
        return []
