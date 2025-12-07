from datetime import datetime, timedelta
import IPython
import copy
import pandas as pd
import numpy as np

from dataclasses import dataclass

@dataclass(frozen=True)
class ExceptionData:
    data: str

class MyException(Exception):
    def __init__(self, exception_details: ExceptionData):
        self.details = exception_details

    def __str__(self):
        return self.details.data


def Eqty_ATM_Optn_Impli_Vol_Smile(debug=False):

    eqty_out = widgets.Output()
    eqty_choice = TextFieldAutosuggest(placeholder='Equity Underlying', filters=['EQ', 'INDX'])
    display(eqty_choice, eqty_out)  # This displays the box

    c_p_select_out = widgets.Output()
    c_p_choice = Select(
        placeholder='Call or Put?', width=300.0)
    c_p_choice.data = [
        {'value': i, 'label': i, 'items': []}
        for i in ['Call', 'Put']]
    # display(c_p_choice, c_p_select_out) # If you want to display each choice box one above the other, you can use this line. I chose `HBox`s instead.

    b_s_select_out = widgets.Output()
    b_s_choice = Select(
        placeholder='Buy or Sell?', width=300.0)
    b_s_choice.data = [
        {'value': i, 'label': i, 'items': []}
        for i in ['Buy', 'Sell']]
    # display(b_s_choice, b_s_select_out) # If you want to display each choice box one above the other, you can use this line. I chose `HBox`s instead.

    # Display both choice boxes (`c_p_choice` & `b_s_choice`) horisontally, next to eachother.
    display(widgets.HBox([c_p_choice, b_s_choice])) # This will display both choice boxes horisontally, next to eachother.

    report_ccy_select_out = widgets.Output()
    report_ccy_choice = Select(
        placeholder='Report Currency?', width=300.0)
    report_ccy_choice.data = [
        {'value': i, 'label': i, 'items': []}
        for i in ['EUR', 'USD', 'GBP', 'JPY']]
    # display(report_ccy_choice, report_ccy_select_out) # If you want to display each choice box one above the other, you can use this line. I chose `HBox`s instead.

    option_price_side_select_out = widgets.Output()
    option_price_side_choice = Select(
        placeholder='Option Price Side?', width=300.0)
    option_price_side_choice.data = [
        {'value': i, 'label': i, 'items': []}
        for i in ['Let Program Choose', 'Bid', 'Ask']]
    # display(option_price_side_choice, option_price_side_select_out) # If you want to display each choice box one above the other, you can use this line. I chose `HBox`s instead.

    # Display both choice boxes (`report_ccy_choice` & `option_price_side_choice`) horisontally, next to eachother.
    display(widgets.HBox([report_ccy_choice, option_price_side_choice]))

    print("\n")
    print("Please enter the RIC of the reference Risk Free Rate, e.g.: for `.SPX`, go with `USDCFCFCTSA3M=`; for `.STOXX50E`, go with `EURIBOR3MD=`")
    rsk_free_rate_prct_out = widgets.Output()
    rsk_free_rate_prct_choice = TextFieldAutosuggest(placeholder='Risk Free Instrument RIC', filters=['FX'])
    display(rsk_free_rate_prct_choice, rsk_free_rate_prct_out)  # This displays the box


    smile_rnge_select_out = widgets.Output()
    smile_rnge_choice = Select(
        placeholder='Smile Moneyness Range', width=300.0)
    smile_rnge_choice.data = [
        {'value': str(i), 'label': str(i), 'items': []}
        for i in range(4)]
    display(smile_rnge_choice, smile_rnge_select_out)


    print("Maturity (note that most Options mature on the third Friday of the month):")
    calendar = Calendar(
        max=(datetime.now() + timedelta(days=30*5)).strftime('%Y-%m-%d'),
        min=(datetime.now() - timedelta(days=30*5)).strftime('%Y-%m-%d'))
    display(calendar)


    widgets.DatePicker(
        description='Start date:', continuous_update=False, max=(datetime.now() + timedelta(days=30*5)).strftime('%Y-%m-%d'))

    # create widgets
    button = Button('Create/Update Graph')
    button_output = widgets.Output()

    loader = Loader(visible=False)
    loader.visible = not loader.visible

    # create click handler
    def click_handler(a):
        with button_output:
            IPython.display.clear_output(wait=True)

            display(loader)

            if c_p_choice.value == "" or eqty_choice.value == "" or rsk_free_rate_prct_choice.value == "" or calendar.value == []:
                IPython.display.clear_output(wait=True)
                raise ValueError("Please make sure to complete all fields before running the program.")

            else:

                if debug:
                    print(f"eqty_choice.value: {eqty_choice.value}")
                    print(f"calendar.value[0]: {calendar.value[0]}")
                    print(f"c_p_choice.value: {c_p_choice.value}")
                    print(f"rsk_free_rate_prct_choice.value: {rsk_free_rate_prct_choice.value}")

                print("This may take a few minutes...")

                # Above, we created an option for the `option_price_side_choice` to allow users to not choose a price side.
                # In the if statement below, we translate this choice to one that the `IPA_Equity_Vola_n_Greeeks` funciton will understand.
                if option_price_side_choice.value == "Let Program Choose":
                    option_price_side_choice_val = None
                else:
                    option_price_side_choice_val = option_price_side_choice.value

                ipa_data = IPA_Equity_Vola_n_Greeeks(
                    debug=debug,
                    underlying=eqty_choice.value,
                    strike=None,
                    maturity=calendar.value[0], # "2024-03-15", # calendar.value,
                    maturity_format = '%Y-%m-%d', # e.g.: '%Y-%m-%d', '%Y-%m-%d %H:%M:%S' or '%Y-%m-%dT%H:%M:%SZ'
                    option_type = c_p_choice.value,
                    buy_sell = b_s_choice.value,
                    curr = report_ccy_choice.value,
                    exercise_style = 'EURO',
                    option_price_side = option_price_side_choice_val,
                    underlying_time_stamp = 'Close',
                    resample = '10min',  # You can consider this the 'bucket' or 'candles' from which calculations will be made.
                    rsk_free_rate_prct = rsk_free_rate_prct_choice.value, # for `".SPX"`, I go with `'USDCFCFCTSA3M='`; for `".STOXX50E"`, I go with `'EURIBOR3MD='`
                    rsk_free_rate_prct_field = 'TR.FIXINGVALUE' # for `".SPX"`, I go with `'TR.FIXINGVALUE'`; for `".STOXX50E"`, I go with `'TR.FIXINGVALUE'` too.
                    ).initiate().get_data()

                sngl_fig, worked = ipa_data.graph(
                    title=ipa_data.ipa_df_gmt_no_na.columns.name).fig, True

                strikes_lst, undrlying_optn_ric_lst, df_gmt_lst, df_lst, fig_lst = ipa_data.cross_moneyness(
                    smile_range=int(smile_rnge_choice.value))

                if debug:
                    print(strikes_lst)
                    display(fig_lst[0])
                    display(fig_lst[-1])

                volatility_result = pd.concat([i.Volatility for i in df_lst], axis=1, join="outer")
                volatility_result.columns = [str(int(i)) for i in strikes_lst]
                volatility_result.index.name = "ImpliedVolatilities"
                volatility_result

                df = volatility_result.copy()
                # Assuming df is your DataFrame and 'timestamp' is your time column
                df['timestamp'] = df.index
                df.timestamp = pd.to_datetime(df.timestamp)
                df.set_index('timestamp', inplace=True)

                # Resample to daily data and compute daily averages
                daily_df = df.resample('7D').mean()

                # Fill NA/NaN values using the specified method
                daily_df_filled = daily_df.fillna(np.nan).astype(float).dropna()
                daily_df_filled.index = [str(i) for i in daily_df_filled.index]
                daily_df_filled = daily_df_filled.T

                # Let's go back to the `sngl_fig` figure created above
                if worked:
                    IPython.display.clear_output(wait=True)
                sngl_fig.show()


                # Now let's get back to our Smile figure:
                smile_fig = go.Figure()

                # Add traces (lines) for each column
                for col in daily_df_filled.columns:
                    smile_fig.add_trace(
                        go.Scatter(
                            x=daily_df_filled.index,
                            y=daily_df_filled[col],
                            mode='lines', name=col))

                smile_fig.update_layout(
                    title="Volatility Smiles",
                    template="plotly_dark")

                smile_fig.show()

    # refister click handler for button
    print("\n")
    button.on_click(click_handler)
    display(button)

    # display our widgets
    display(button_output)