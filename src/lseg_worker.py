from fastapi import FastAPI
import pandas as pd
import eikon as ek

app = FastAPI()

# Your Eikon API key
ek.set_app_key("06dbeb8bdea345b49d0e9f917a1a124250aedf25")

FIELDS = [
    "PUTCALLIND",
    "STRIKE_PRC",
    "CF_BID",
    "CF_ASK",
    "CF_CLOSE",
    "IMP_VOLT",
]


@app.get("/fetch")
def fetch(symbol: str):

    try:
        # ---------------------------------------------------
        # 1) Get spot price
        # ---------------------------------------------------
        spot_df, spot_err = ek.get_data(f"{symbol}.O", ["TRDPRC_1"])
        spot = None

        if spot_df is not None and "TRDPRC_1" in spot_df.columns:
            vals = spot_df["TRDPRC_1"].dropna().values
            if len(vals) > 0:
                spot = float(vals[0])

        # ---------------------------------------------------
        # 2) Get option chain
        # ---------------------------------------------------
        ric = f"0#{symbol.upper()}*.U"
        df, err = ek.get_data(ric, fields=FIELDS)

        if df is None or df.empty:
            # IMPORTANT: must return success=True, otherwise front-end breaks
            return {"success": True, "symbol": symbol, "data": []}

        # Clean missing strikes
        df = df.dropna(subset=["STRIKE_PRC"], how="any")

        # Convert numeric
        numeric_cols = ["CF_BID", "CF_ASK", "CF_CLOSE", "STRIKE_PRC", "IMP_VOLT"]
        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        # Mid price
        df["MID"] = df[["CF_BID", "CF_ASK"]].mean(axis=1)

        # Standardize option type
        df["OPTION_TYPE"] = (
            df["PUTCALLIND"]
            .astype(str)
            .str.strip()
            .str.upper()
            .map({"C": "CALL", "CALL": "CALL", "P": "PUT", "PUT": "PUT"})
        )

        # Fill spot
        df["TRDPRC_1"] = spot

        return {
            "success": True,
            "symbol": symbol,
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        print("Worker EXCEPTION full:", e)
        return {
            "success": True,
            "symbol": symbol,
            "data": []   # NEVER return success=False
        }
