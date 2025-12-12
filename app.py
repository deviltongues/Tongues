# app.py
from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
from shiny import App, ui, render, reactive, req
import refinitiv.data as rd


# ---------- helpers ----------
def get_next_friday(d: datetime.date) -> datetime.date:
    return d + timedelta(days=(4 - d.weekday()) % 7)

def get_fourth_friday(d: datetime.date) -> datetime.date:
    return get_next_friday(d) + timedelta(weeks=3)

today = datetime.today().date()
default_min_expiry = get_next_friday(today)
default_max_expiry = today + timedelta(days=120)  # safe default

def build_surface_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Bid"] = pd.to_numeric(df.get("Bid"), errors="coerce")
    df["Ask"] = pd.to_numeric(df.get("Ask"), errors="coerce")
    df["Last"] = pd.to_numeric(df.get("Last"), errors="coerce")

    df["mid"] = df[["Bid", "Ask"]].mean(axis=1)
    df.loc[df["mid"].isna(), "mid"] = df["Last"]

    df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"])
    now = pd.Timestamp.today()
    df["T"] = (df["ExpiryDate"] - now).dt.days / 365.0
    df["K"] = df["StrikePrice"]

    return df[["RIC", "K", "T", "mid", "StrikePrice", "ExpiryDate", "CallPutOption"]]


# ---------- UI ----------
app_ui = ui.page_fillable(
    ui.include_css("custom.css"),
    ui.div(
        {"class": "container-fluid"},
        ui.div(
            {"class": "row", "style": "margin-top: 30px;"},
            ui.div(
                {"class": "col-md-3"},
                ui.input_selectize(
                    "underlying_ric",
                    "Underlying Asset RIC",
                    choices=[
                        "AAPL.O", "MSFT.O", "TSLA.O", "NVDA.O",
                        "AMZN.O", "META.O", "GOOGL.O", "NFLX.O",
                        "AMD.O", "INTC.O", "JPM.N", "GS.N",
                    ],
                    selected="MSFT.O",
                    options={"maxItems": 1},
                ),
                ui.input_action_button(
                    "fetch_spot", "FETCH SPOT", class_="w-100", style="margin-top: 12px;"
                ),
                ui.div(
                    {"style": "margin-top: 20px;"},
                    ui.input_numeric("min_strike", "Min Strike", value=300),
                    ui.input_numeric("max_strike", "Max Strike", value=500),
                    ui.input_date("min_expiry", "Min Expiry", value=default_min_expiry),
                    ui.input_date("max_expiry", "Max Expiry", value=default_max_expiry),
                    ui.input_numeric("top_options", "Max Contracts", value=1000),
                ),
                ui.input_action_button(
                    "fetch_chain", "SCAN OPTIONS", class_="w-100", style="margin-top: 20px;"
                ),
            ),
            ui.div(
                {"class": "col-md-9"},
                ui.h4("Spot Price"),
                ui.output_text("spot_price"),
                ui.output_text("exchange_time"),
                ui.h4("Options Chain"),
                ui.output_data_frame("options_table"),
            ),
        ),
    ),
)


# ---------- server ----------
def server(input, output, session):
    rd.open_session()
    session.on_ended(rd.close_session)

    spot_price_data = reactive.Value(None)
    exchange_time_data = reactive.Value(None)
    option_data = reactive.Value(None)
    surface_data = reactive.Value(None)

    # ---- spot ----
    @reactive.effect
    @reactive.event(input.fetch_spot)
    def _fetch_spot():
        ric = input.underlying_ric()
        df = rd.get_data(ric, fields=["TR.PriceClose", "CF_TIME"])
        spot_price_data.set(df["Price Close"].iloc[0])
        exchange_time_data.set(df["CF_TIME"].iloc[0])

    @render.text
    def spot_price():
        req(spot_price_data.get() is not None)
        return f"Spot Price: ${spot_price_data.get():.2f}"

    @render.text
    def exchange_time():
        req(exchange_time_data.get() is not None)
        return f"Exchange Time: {exchange_time_data.get()}"

    # ---- chain + prices ----
    @reactive.effect
    @reactive.event(input.fetch_chain)
    def _fetch_chain():
        ric = input.underlying_ric()

        filter_str = (
            "( SearchAllCategoryv2 eq 'Options' and "
            f"(ExpiryDate gt {input.min_expiry()} and ExpiryDate lt {input.max_expiry()}) and "
            f"(StrikePrice ge {input.min_strike()} and StrikePrice le {input.max_strike()}) and "
            "ExchangeName xeq 'OPRA' and "
            f"(UnderlyingQuoteRIC eq '{ric}'))"
        )

        chain = rd.discovery.search(
            view=rd.discovery.Views.EQUITY_QUOTES,
            top=input.top_options(),
            filter=filter_str,
            select="RIC,CallPutOption,StrikePrice,ExpiryDate",
        )

        if chain.empty:
            option_data.set(chain)
            surface_data.set(None)
            return

        chain["RIC"] = chain["RIC"].astype(str)

        # Robust RIC extraction from price dataframe
        raw_price = rd.get_data(
            universe=chain["RIC"].tolist(),
            fields=["CF_BID", "CF_ASK", "CF_LAST"],
        ).reset_index()

        # Pick the column that actually holds the instrument/ric
        candidate_cols = ["RIC", "Instrument", "ric", "instrument", "index"]
        ric_col = None
        for c in candidate_cols:
            if c in raw_price.columns:
                ric_col = c
                break
        if ric_col is None:
            # fall back to first column
            ric_col = raw_price.columns[0]

        price_df = raw_price.rename(
            columns={
                ric_col: "RIC",
                "CF_BID": "Bid",
                "CF_ASK": "Ask",
                "CF_LAST": "Last",
            }
        )[["RIC", "Bid", "Ask", "Last"]]

        price_df["RIC"] = price_df["RIC"].astype(str)

        merged = chain.merge(price_df, on="RIC", how="left")
        option_data.set(merged)

        surf = build_surface_df(merged)
        surface_data.set(surf)

    @render.data_frame
    def options_table():
        df = option_data.get()
        req(df is not None)
        return df


app = App(app_ui, server)
