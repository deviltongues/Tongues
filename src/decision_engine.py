import math
from typing import Dict, Any, List
import numpy as np

RISK_FREE_RATE = 0.05
THRESHOLD = 0.02


def compute_implied_r(S, C, P, K, T):
    try:
        if T <= 0:
            return None
        numerator = S - (C - P)
        if numerator <= 0 or K <= 0:
            return None

        r = - (1.0 / T) * math.log(numerator / K)

        if np.isnan(r) or np.isinf(r):
            return None

        return float(r)
    except Exception:
        return None


def analyze_chain(records: list,
                  base_rate: float = RISK_FREE_RATE,
                  threshold: float = THRESHOLD) -> Dict[str, Any]:

    signals = []
    rows = []

    T = 30 / 365.0  # fixed 30D expiry

    # Convert list of dicts into strike groups
    by_strike = {}
    for r in records:
        K = r.get("STRIKE_PRC")
        if K not in by_strike:
            by_strike[K] = {"CALL": None, "PUT": None, "spot": r.get("TRDPRC_1")}
        opt_type = r.get("OPTION_TYPE")
        if opt_type in ["CALL", "PUT"]:
            by_strike[K][opt_type] = r

    for K in sorted(by_strike.keys()):
        data = by_strike[K]
        call = data["CALL"]
        put = data["PUT"]
        S = data["spot"]

        if call is None or put is None or S is None:
            continue

        C = call.get("MID")
        P = put.get("MID")

        r = compute_implied_r(S, C, P, K, T)

        row = {
            "strike": K,
            "call_mid": C,
            "put_mid": P,
            "implied_r": r,
            "signal": None
        }

        # arbitrage condition
        if r is not None:
            diff = r - base_rate

            if diff > threshold:
                row["signal"] = "Sell synthetic, buy stock"
                signals.append(row.copy())
            elif diff < -threshold:
                row["signal"] = "Buy synthetic, short stock"
                signals.append(row.copy())

        rows.append(row)

    return {
        "signals": signals,
        "rows": rows,
        "base_rate": base_rate,
        "threshold": threshold,
    }
