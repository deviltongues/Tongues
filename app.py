from shiny import App, render, ui, reactive, req
import refinitiv.data as rd
from datetime import datetime, timedelta


# --- Date helpers ---

def get_next_friday(d):
    return d + timedelta(days=(4 - d.weekday()) % 7)

def get_fourth_friday(d):
    return get_next_friday(d) + timedelta(weeks=3)

today = datetime.today().date()
default_min_expiry = get_next_friday(today)
default_max_expiry = get_fourth_friday(today)


# --- UI ---

app_ui = ui.page_fillable(
    ui.include_css("custom.css"),
    ui.include_js("custom.js"),

    ui.div({"class": "container-fluid"},
        ui.div({"class": "row", "style": "margin-top: 30px;"},

            ui.div({"class": "col-md-3"},
                ui.input_selectize(
                    "underlying_ric",
                    "Underlying Asset RIC",
                    choices=[
                        "AAPL.O", "MSFT.O", "TSLA.O", "NVDA.O",
                        "AMZN.O", "META.O", "GOOGL.O", "NFLX.O",
                        "AMD.O", "INTC.O", "JPM.N", "GS.N"
                    ],
                    selected="MSFT.O",
                    options={"maxItems": 1}
                ),

                ui.input_action_button(
                    "fetch_spot", "FETCH SPOT",
                    class_="w-100", style="margin-top: 12px;"
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
                    class_="w-100", style="margin-top: 20px;"
                )
            ),

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


# --- Server ---

def server(input, output, session):

    rd.open_session()
    session.on_ended(rd.close_session)

    spot_price_data = reactive.Value(None)
    exchange_time_data = reactive.Value(None)
    option_data = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.fetch_spot)
    def fetch_spot():
        ric = input.underlying_ric()
        spot_df = rd.get_data(ric, fields=["TR.PriceClose", "CF_TIME"])

        spot_price_data.set(spot_df["Price Close"].iloc[0])
        exchange_time_data.set(spot_df["CF_TIME"].iloc[0])

    @render.text
    def spot_price():
        req(spot_price_data.get() is not None)
        return f"Spot Price: ${spot_price_data.get():.2f}"

    @render.text
    def exchange_time():
        req(exchange_time_data.get() is not None)
        return f"Exchange Time: {exchange_time_data.get()}"

    @reactive.effect
    @reactive.event(input.fetch_chain)
    def fetch_chain():

        ric = input.underlying_ric()

        filter_str = (
            "( SearchAllCategoryv2 eq 'Options' and "
            f"(ExpiryDate gt {input.min_expiry()} and "
            f"ExpiryDate lt {input.max_expiry()}) and "
            f"(StrikePrice ge {input.min_strike()} and "
            f"StrikePrice le {input.max_strike()}) and "
            "ExchangeName xeq 'OPRA' and "
            f"(UnderlyingQuoteRIC eq '{ric}'))"
        )

        df = rd.discovery.search(
            view=rd.discovery.Views.EQUITY_QUOTES,
            top=input.top_options(),
            filter=filter_str,
            select="RIC,CallPutOption,StrikePrice,ExpiryDate"
        )

        option_data.set(df)

    @render.data_frame
    def options_table():
        req(option_data.get() is not None and not option_data.get().empty)
        return option_data.get()


# --- App ---

app = App(app_ui, server)
app.run()
