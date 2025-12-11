from shiny import App, render, ui, reactive, req
import refinitiv.data as rd
import pandas as pd
from datetime import datetime, timedelta


# -----------------------------
# Helpers for default expiry
# -----------------------------
def get_next_friday(d):
    return d + timedelta(days=(4 - d.weekday()) % 7)

def get_fourth_friday(d):
    return get_next_friday(d) + timedelta(weeks=3)

today = datetime.today().date()
default_min_expiry = get_next_friday(today)
default_max_expiry = today + timedelta(days=120)    # safer default


# -----------------------------
# Build surface-ready df
# -----------------------------
def build_surface_df(df):
    df = df.copy()

    # mid price
    df["mid"] = (df["Bid"] + df["Ask"]) / 2

    # time to expiry T
    df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"])
    now = pd.Timestamp.today()
    df["T"] = (df["ExpiryDate"] - now).dt.days / 365.0

    df["K"] = df["StrikePrice"]

    return df[["RIC", "K", "T", "mid", "StrikePrice", "ExpiryDate", "CallPutOption"]]


# -----------------------------
# UI
# -----------------------------
app_ui = ui.page_fillable(
    ui.include_css("custom.css"),

    ui.div({"class": "container-fluid"},
        ui.div({"class": "row", "style": "margin-top: 30px;"},

            # Left control panel
            ui.div({"class": "col-md-3"},
                ui.input_selectize(
                    "underlying_ric",
                    "Underlying Asset RIC",
                    choices=[
                        "AAPL.O", "MSFT.O", "TSLA.O", "NVDA.O",
                        "AMZN.O", "META.O", "GOOGL.O", "NFLX.O",
                        "AMD.O", "INTC.O", "JPM.N", "GS.N"
                    ],
                    selected="MSFT.O"
                ),

                ui.input_action_button(
                    "fetch_spot", "FETCH SPOT",
                    class_="w-100",
                    style="margin-top: 12px;"
                ),

                ui.div({"style": "margin-top: 20px;"},
                    ui.input_numeric("min_strike", "Min Strike", value=300),
                    ui.input_numeric("max_strike", "Max Strike", value=500),
                    ui.input_date("min_expiry", "Min Expiry", value=default_min_expiry),
                    ui.input_date("max_expiry", "Max Expiry", value=default_max_expiry),
                    ui.input_numeric("top_options", "Max Contracts", value=1000)
                ),

                ui.input_action_button(
                    "fetch_chain", "SCAN OPTIONS",
                    class_="w-100",
                    style="margin-top: 20px;"
                )
            ),

            # Right panel
            ui.div({"class": "col-md-9"},
                ui.h4("Spot Price"),
                ui.output_text("spot_price"),
                ui.output_text("exchange_time"),

                ui.h4("Options Chain"),
                ui.output_data_frame("options_table")
            )
        )
    )
)


# -----------------------------
# SERVER
# -----------------------------
def server(input, output, session):

    rd.open_session()
    session.on_ended(rd.close_session)

    spot_price_data = reactive.Value(None)
    exchange_time_data = reactive.Value(None)
    option_data = reactive.Value(None)
    surface_data = reactive.Value(None)


    # -----------------------------
    # Fetch spot price
    # -----------------------------
    @reactive.effect
    @reactive.event(input.fetch_spot)
    def fetch_spot():
        ric = input.underlying_ric()
        print("\n=== FETCHING SPOT FOR:", ric)

        df = rd.get_data(ric, fields=["TR.PriceClose", "CF_TIME"])
        print(df)

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


    # -----------------------------
    # Fetch options chain + price
    # -----------------------------
    @reactive.effect
    @reactive.event(input.fetch_chain)
    def fetch_chain():
        ric = input.underlying_ric()

        # Build filter
        filter_str = (
            "( SearchAllCategoryv2 eq 'Options' and "
            f"(ExpiryDate gt {input.min_expiry()} and "
            f"ExpiryDate lt {input.max_expiry()}) and "
            f"(StrikePrice ge {input.min_strike()} and "
            f"StrikePrice le {input.max_strike()}) and "
            "ExchangeName xeq 'OPRA' and "
            f"(UnderlyingQuoteRIC eq '{ric}'))"
        )

        print("\n=== OPTION SEARCH FILTER ===")
        print(filter_str)

        chain = rd.discovery.search(
            view=rd.discovery.Views.EQUITY_QUOTES,
            top=input.top_options(),
            filter=filter_str,
            select="RIC,CallPutOption,StrikePrice,ExpiryDate"
        )

        print("\n=== RAW CHAIN ===")
        print(chain.head(), chain.shape)

        if chain.empty:
            print("⚠ WARNING: chain empty — no contracts match filter")
            option_data.set(chain)
            surface_data.set(None)
            return

        # Ensure RIC is string
        chain["RIC"] = chain["RIC"].astype(str)

        # Fetch OPRA option prices (CF_BID / CF_ASK / CF_LAST)
        price_df = rd.get_data(
            universe=chain["RIC"].tolist(),
            fields=["CF_BID", "CF_ASK", "CF_LAST"]
        )

        price_df = price_df.reset_index().rename(columns={"index": "RIC"})
        price_df["RIC"] = price_df["RIC"].astype(str)

        price_df = price_df.rename(columns={
            "CF_BID": "Bid",
            "CF_ASK": "Ask",
            "CF_LAST": "Last"
        })

        print("\n=== PRICE DF ===")
        print(price_df.head(), price_df.shape)

        # Merge prices
        merged = chain.merge(price_df, on="RIC", how="left")
        print("\n=== MERGED DF ===")
        print(merged.head(), merged.shape)

        option_data.set(merged)

        # Surface
        surf = build_surface_df(merged)
        surface_data.set(surf)


    # -----------------------------
    # Render chain table
    # -----------------------------
    @render.data_frame
    def options_table():
        df = option_data.get()
        req(df is not None)
        return df


# -----------------------------from shiny import App, render, ui, reactive, req
# import refinitiv.data as rd
# import pandas as pd
# from datetime import datetime, timedelta
#
#
# # ========== CONFIG ==========
# DEBUG = True   # 设置 False 可以关闭所有调试输出
# # ============================
#
#
# # --- Date helpers ---
#
# def get_next_friday(d):
#     return d + timedelta(days=(4 - d.weekday()) % 7)
#
# def get_fourth_friday(d):
#     return get_next_friday(d) + timedelta(weeks=3)
#
# today = datetime.today().date()
# default_min_expiry = get_next_friday(today)
# default_max_expiry = get_fourth_friday(today)
#
#
# # --- Build surface DF (T, K, mid) ---
#
# def build_surface_df(df):
#     df = df.copy()
#
#     # 若 Bid 或 Ask 缺失，用 Last 代替
#     df["Bid"] = pd.to_numeric(df["Bid"], errors="coerce")
#     df["Ask"] = pd.to_numeric(df["Ask"], errors="coerce")
#     df["Last"] = pd.to_numeric(df["Last"], errors="coerce")
#
#     df["mid"] = df[["Bid", "Ask"]].mean(axis=1)
#     df.loc[df["mid"].isna(), "mid"] = df["Last"]
#
#     df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"])
#     now = pd.Timestamp.today()
#     df["T"] = (df["ExpiryDate"] - now).dt.days / 365
#     df["K"] = df["StrikePrice"]
#
#     return df[["K", "T", "mid", "RIC", "CallPutOption", "StrikePrice", "ExpiryDate"]]
#
#
# # --- UI ---
#
# app_ui = ui.page_fillable(
#     ui.include_css("custom.css"),
#     ui.include_js("custom.js"),
#
#     ui.div({"class": "container-fluid"},
#         ui.div({"class": "row", "style": "margin-top: 30px;"},
#
#             # --- Left Panel ---
#             ui.div({"class": "col-md-3"},
#                 ui.input_selectize(
#                     "underlying_ric",
#                     "Underlying Asset RIC",
#                     choices=[
#                         "AAPL.O", "MSFT.O", "TSLA.O", "NVDA.O",
#                         "AMZN.O", "META.O", "GOOGL.O", "NFLX.O",
#                         "AMD.O", "INTC.O", "JPM.N", "GS.N"
#                     ],
#                     selected="MSFT.O",
#                     options={"maxItems": 1}
#                 ),
#
#                 ui.input_action_button(
#                     "fetch_spot", "FETCH SPOT",
#                     class_="w-100", style="margin-top: 12px;"
#                 ),
#
#                 ui.div({"style": "margin-top: 20px;"},
#                     ui.input_numeric("min_strike", "Min Strike", value=300),
#                     ui.input_numeric("max_strike", "Max Strike", value=500),
#                     ui.input_date("min_expiry", "Min Expiry", value=default_min_expiry),
#                     ui.input_date("max_expiry", "Max Expiry", value=default_max_expiry),
#                     ui.input_numeric("top_options", "Max Contracts", value=1000)
#                 ),
#
#                 ui.input_action_button(
#                     "fetch_chain", "SCAN OPTIONS",
#                     class_="w-100", style="margin-top: 20px;"
#                 )
#             ),
#
#             # --- Right Panel ---
#             ui.div({"class": "col-md-9"},
#                 ui.h4("Spot Price"),
#                 ui.output_text("spot_price"),
#                 ui.output_text("exchange_time"),
#
#                 ui.h4("Options Chain"),
#                 ui.output_data_frame("options_table")
#             )
#         )
#     )
# )
#
#
# # --- Server ---
#
# def server(input, output, session):
#
#     rd.open_session()
#     session.on_ended(rd.close_session)
#
#     spot_price_data = reactive.Value(None)
#     exchange_time_data = reactive.Value(None)
#     option_data = reactive.Value(None)
#     surface_data = reactive.Value(None)
#
#
#     # --- Spot Fetch ---
#     @reactive.effect
#     @reactive.event(input.fetch_spot)
#     def fetch_spot():
#         ric = input.underlying_ric()
#         if DEBUG: print(f"\n=== FETCHING SPOT FOR: {ric}")
#
#         df = rd.get_data(ric, fields=["TR.PriceClose", "CF_TIME"])
#
#         if DEBUG: print(df)
#
#         spot_price_data.set(df["Price Close"].iloc[0])
#         exchange_time_data.set(df["CF_TIME"].iloc[0])
#
#
#     @render.text
#     def spot_price():
#         req(spot_price_data.get() is not None)
#         return f"Spot Price: ${spot_price_data.get():.2f}"
#
#
#     @render.text
#     def exchange_time():
#         req(exchange_time_data.get() is not None)
#         return f"Exchange Time: {exchange_time_data.get()}"
#
#
#     # --- Options chain fetch ---
#     @reactive.effect
#     @reactive.event(input.fetch_chain)
#     def fetch_chain():
#
#         ric = input.underlying_ric()
#         minE = input.min_expiry()
#         maxE = input.max_expiry()
#         minK = input.min_strike()
#         maxK = input.max_strike()
#         topN = input.top_options()
#
#         filter_str = (
#             "( SearchAllCategoryv2 eq 'Options' and "
#             f"(ExpiryDate gt {minE} and ExpiryDate lt {maxE}) and "
#             f"(StrikePrice ge {minK} and StrikePrice le {maxK}) and "
#             "ExchangeName xeq 'OPRA' and "
#             f"(UnderlyingQuoteRIC eq '{ric}'))"
#         )
#
#         if DEBUG:
#             print("\n=== OPTION SEARCH FILTER ===")
#             print(filter_str)
#
#         chain = rd.discovery.search(
#             view=rd.discovery.Views.EQUITY_QUOTES,
#             top=topN,
#             filter=filter_str,
#             select="RIC,CallPutOption,StrikePrice,ExpiryDate"
#         )
#
#         if DEBUG:
#             print("\n=== RAW CHAIN ===")
#             print(chain.head(), chain.shape)
#
#         if chain.empty:
#             option_data.set(chain)
#             surface_data.set(None)
#             return
#
#         # ===== PRICE FETCH =====
#         raw_price_df = rd.get_data(
#             universe=chain["RIC"].tolist(),
#             fields=["CF_BID", "CF_ASK", "CF_LAST"]
#         )
#
#         # Reset index -> Instrument column
#         raw_price_df = raw_price_df.reset_index().rename(columns={"index": "Instrument"})
#
#         # True RIC is inside "Instrument"
#         raw_price_df["RIC"] = raw_price_df["Instrument"].astype(str)
#
#         # Keep columns we want
#         price_df = raw_price_df[["RIC", "CF_BID", "CF_ASK", "CF_LAST"]].rename(
#             columns={"CF_BID": "Bid", "CF_ASK": "Ask", "CF_LAST": "Last"}
#         )
#
#         if DEBUG:
#             print("\n=== PRICE DF ===")
#             print(price_df.head(), price_df.shape)
#
#         # ===== MERGE =====
#         merged = chain.merge(price_df, on="RIC", how="left")
#
#         if DEBUG:
#             print("\n=== MERGED DF ===")
#             print(merged.head(), merged.shape)
#
#         option_data.set(merged)
#
#         # Build surface (for tomorrow’s 3D chart)
#         surf = build_surface_df(merged)
#         surface_data.set(surf)
#
#
#     @render.data_frame
#     def options_table():
#         df = option_data.get()
#         req(df is not None and not df.empty)
#         return df
#
#
#
# # --- Run App ---
#
# app = App(app_ui, server)
# app.run()
# Run App
# -----------------------------
app = App(app_ui, server)
app.run()
